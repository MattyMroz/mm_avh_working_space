# architektura potokowa + inne zyski wydajności

> tryb: big ideate | data: 2026-07-07
> temat: przebudowa trybu auto na pipeline stages (osobne potoki działające
> jednocześnie, odcinki płyną jak taśma), + polowanie na inne zyski wydajności

---

## 🎯 Definicja Problemu

Tryb auto przetwarza N odcinków MKV **sekwencyjnie etap-po-etapie**: wszystkie przez
extract, potem wszystkie przez translate, potem audio, potem merge. Zmierzono: 5:44 → 5:02
po zrównolegleniu wypakowywania (10 plików).

**Wąskie gardło:** translate (Google API) i audio (ElevenBytes API) — limitowane przez
serwery zewnętrzne. Jednego odcinka nie da się przyspieszyć (limit API to fizyczna granica).

**Insight użytkownika (sedno):** choć nie przeskoczymy czasu API dla *jednego* odcinka, można
**nałożyć martwe czasy oczekiwania różnych odcinków na siebie**. Gdy odcinek 1 czeka na TTS,
odcinek 2 może się tłumaczyć (inne API — Google vs ElevenBytes, nie konkurują o ten sam limit).
To architektura **potokowa (pipeline stages)**: osobne potoki extract/translate/audio/merge
działają jednocześnie, odcinki płyną przez nie jak taśma produkcyjna.

**Cel:** wall-clock całości ≈ max(suma_najdłuższego_potoku) zamiast sumy wszystkich etapów.

## 📐 Tablica Prawdy (Constraints)

| # | Święta Zasada (Non-Negotiable) | Źródło | Status |
|---|-------------------------------|--------|--------|
| 1 | Nie łamać limitów API (w danym potoku 1 rzecz naraz albo obecna współbieżność) | user | 🔒 ABSOLUTNA |
| 2 | Izolacja błędów: padnięcie 1 odcinka NIE przerywa potoku ani innych odcinków | user | 🔒 ABSOLUTNA |
| 3 | Kolejność FIFO w potoku (potok przetwarza iteracyjnie) | user | 🔒 ABSOLUTNA |
| 4 | Foldery per-odcinek — zero nadpisywania plików między odcinkami | user | 🔒 ABSOLUTNA |
| 5 | Równoległość skalowana do cpu_count (nie hardcode) | user | 🔒 ABSOLUTNA |
| 6 | Tylko tryb auto — tryb manualny (interaktywny) bez zmian | user+repo | 🔒 ABSOLUTNA |
| 7 | Komentarze po angielsku; Python instructions (ThreadPool I/O, typing.List, guard) | user+repo | 🔒 ABSOLUTNA |
| 8 | Nie zepsuć istniejącego cache/retry (elevenbytes survive-crash, rundy) | repo | 🔒 ABSOLUTNA |

---

## 🧱 Fundament: co wiemy z mapy kodu (Faza 0)

**Dobra wiadomość:** wszystkie klasy (`SubtitleToSpeech`, `MkvToolNix`, `SubtitleRefactor`,
`MKVProcessing`) to `@dataclass` z polami-ścieżkami (defaulty = globalne stałe). Metody używają
`self.working_space_temp`, NIE stałych na sztywno. → per-odcinek ścieżki wstrzykuje się przez
konstruktor, bez zmiany ciała metod.

**Blokery równoległości (kolizje na wspólnym folderze) — z mapy:**
1. Nazwy generyczne: `temp/temp.wav` (harpo), `temp/pp_speed_*.wav`, `temp/bal_pp_*.wav`
2. `_elevenbytes_cache/{idx:04d}.mp3` — wspólny cache indeksowany numerem linii bez nazwy
   odcinka → dwa odcinki nadpisują sobie MP3 + wzajemne `rmtree`
3. `merge_tts_audio`/`_get_files_dict` — `listdir` po CAŁYM temp+main_subs, iteracja po
   wszystkich odcinkach, wzajemne usuwanie plików (SEDNO problemu)
4. Etapy batchowe w start.py — `get_srt_files(MAIN_SUBS)` itd. iterują cały folder

**Bez zmian:** `track_selector.py`, `style_classifier.py` (brak I/O), `translator.py` (metody
biorą `dir_path` argumentem).

---

## 📊 Profil czasowy (fundament decyzji — HIPOTEZA, do potwierdzenia pomiarem)

Pipelining ma sens TYLKO jeśli etapy mają porównywalny czas ORAZ dużo czekania I/O. Dodany
już pomiar per-etap (`_timed_stage`) odpowie. Hipoteza dla 10 odcinków z 5:02:

| Potok | Natura | Szac. udział | Czeka na co | Nakładalny? |
|-------|--------|-------------|-------------|-------------|
| Extract | I/O+subprocess | ~15-25% | dysk/mkvextract | ✅ (już równoległy) |
| Translate | sieć (Google API) | ~20-30% | odpowiedź API | ✅✅ (dużo idle) |
| Audio | sieć (ElevenBytes, 85 req/odc) | ~30-45% | odpowiedź API | ✅✅ (dużo idle) |
| Merge | CPU/IO (ffmpeg eac3) | ~10-20% | ffmpeg | ✅ |
| Refactor/reszta | CPU lekki | <5% | — | — |

**Kluczowa obserwacja:** translate i audio to głównie **czekanie na sieć** (idle CPU). To
IDEALNI kandydaci do nakładania — gdy jeden czeka, drugi pracuje. Tu jest realny zysk.

---

## 💡 Dywergencja — Pomysły

### 🚀 GRUPA A: Architektura potokowa (główny temat)

### 💡 A1: Pełny pipeline z bounded queues (producer-consumer)
**Opis:** 4 potoki (extract→translate→audio→merge) jako osobne wątki/workery, połączone
kolejkami `queue.Queue(maxsize=N)`. Odcinek po ukończeniu etapu ląduje w kolejce następnego.
**Mechanizm:** Każdy potok = pętla `while: item = queue.get(); process(item); next_queue.put(item)`.
Potoki żyją równolegle (ThreadPool per potok lub 1 wątek/potok). Bariera na końcu.
**Mocne:** Klasyczny, sprawdzony wzorzec. Maksymalne nakładanie. FIFO naturalne (Queue).
Izolacja błędów: try/except w pętli potoku → błędny item pomijany, potok żyje dalej.
**Słabe:** Złożoność orkiestracji. Przeplot logów. Trudniejszy debug. Foldery per-odcinek
wymagane (constraint #4).
**Ryzyko:** Deadlock jeśli źle z maxsize. Błąd w potoku musi być łapany per-item (constraint #2).
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — właściwy wzorzec, ale wymaga dyscypliny.
**Test tablicy prawdy:** ✅ (przy poprawnej izolacji błędów i folderach per-odcinek)

### 💡 A2: Uproszczony pipeline — nakładanie sąsiednich etapów (audio||merge, translate||audio)
**Opis:** Nie pełne 4 potoki, tylko "gdy odcinek kończy etap N, jego etap N+1 startuje w tle,
a główna pętla bierze następny odcinek do etapu N".
**Mechanizm:** ThreadPoolExecutor jako "tło" — `executor.submit(merge, odcinek)` po audio,
`as_completed` na końcu. Mniej potoków, prostsze.
**Mocne:** Prostsze niż A1, mniej ryzyka deadlocku. Łatwiej dodawać etapami.
**Słabe:** Mniejsze nakładanie niż pełny pipeline (nie wszystkie 4 naraz).
**Ryzyko:** Średnie.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — dobry kompromis złożoność/zysk.
**Test tablicy prawdy:** ✅

### 💡 A3: asyncio pipeline (async/await + asyncio.Queue)
**Opis:** Całość jako asyncio z kolejkami async. Naturalny dla I/O-bound (sieć).
**Mechanizm:** `asyncio.Queue`, `asyncio.gather` na potokach, `to_thread` dla blocking (ffmpeg).
**Mocne:** Elegancki dla sieci. audio już częściowo async (httpx w tts_elevenbytes).
**Słabe:** ⚠️ Duża przebudowa. Miesza się z ThreadPool (ElevenBytes używa sync+thread pod
spodem). Ryzyko event-loop hell (Windows Selector policy już jest). Krzywa uczenia.
**Ryzyko:** WYSOKIE — istniejący kod jest sync/thread, nie async.
**Ocena:** ⭐⭐⭐⭐⭐☆☆☆☆☆ (5/10) — teoretycznie ładne, praktycznie ryzykowne w tym kodzie.
**Test tablicy prawdy:** ⚠️ ryzyko #8 (może zepsuć istniejący retry/cache)

### 💡 A4: Batch-parallel per etap (bez pipeline — po prostu N odcinków naraz w etapie)
**Opis:** Nie pipeline, ale: translate 3 odcinki naraz, potem audio 3 naraz, potem merge.
**Mechanizm:** ThreadPoolExecutor w każdym etapie osobno (jak zrobiono z extract).
**Mocne:** Najprostsze rozszerzenie tego co już jest (extract już tak działa).
**Słabe:** NIE nakłada różnych etapów — tłumaczenie nie idzie równolegle z audio. Bariera
między etapami. Mniejszy zysk niż pipeline.
**Ryzyko:** Niskie. Ale audio API — 3 odcinki × 85 req = 255 req naraz → ryzyko 500/ban.
**Ocena:** ⭐⭐⭐⭐⭐⭐☆☆☆☆ (6/10) — bezpieczne, ale nie realizuje wizji nakładania etapów.
**Test tablicy prawdy:** ⚠️ #1 (255 req naraz może łamać limit API)

### 🛠️ GRUPA B: Inne zyski wydajności (poza pipeliningiem)

### 💡 B1: Cache oryginalnego audio bez re-ekstrakcji (pominięcie mkvextract przy retry)
**Opis:** Wyekstrahowany `.aac`/`.ac3` z MKV zostaje — jeśli istnieje i jest OK, nie
ekstrahuj ponownie przy powtórnym uruchomieniu.
**Mechanizm:** Sprawdź `path.exists + rozmiar > threshold` przed mkvextract.
**Mocne:** Przy powtórnych biegach (a robisz je często!) oszczędza CAŁY etap extract.
**Słabe:** Trzeba uważać na niekompletne pliki (walidacja rozmiaru/duration).
**Ryzyko:** Niskie (guard na rozmiar).
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — tani zysk przy Twoim wzorcu pracy (wielokrotne biegi).
**Test tablicy prawdy:** ✅

### 💡 B2: Współbieżne tłumaczenie w obrębie 1 odcinka (chunki napisów równolegle)
**Opis:** Google Translate tłumaczy paczkami linii. Wysyłaj kilka paczek jednego odcinka
równolegle zamiast sekwencyjnie.
**Mechanizm:** ThreadPool na chunkach translate w translator.py.
**Mocne:** Przyspiesza tłumaczenie POJEDYNCZEGO odcinka (nie tylko między odcinkami).
**Słabe:** ⚠️ Google Translate ma rate limit — zbyt wiele równoległych = 429/ban. Ryzyko #1.
**Ryzyko:** ŚREDNIE-WYSOKIE (limit API to święta zasada).
**Ocena:** ⭐⭐⭐⭐☆☆☆☆☆☆ (4/10) — kusi, ale drażni limit API.
**Test tablicy prawdy:** ⚠️ #1

### 💡 B3: Pomiń re-generację audio dla już gotowych linii globalnie (persistent cache)
**Opis:** Cache MP3 ElevenBytes przetrwa między biegami (nie tylko w obrębie 1 uruchomienia).
**Mechanizm:** Klucz cache = hash(tekst+głos+engine) zamiast indeksu linii. Zapisany trwale.
**Mocne:** Ten sam tekst (powtórki fraz, wielokrotne biegi) = zero re-syntezy. Duży zysk przy
retry po awarii.
**Słabe:** Zarządzanie cache (rozmiar, invalidacja). Zmiana klucza z indeksu na hash.
**Ryzyko:** Średnie (więcej stanu do utrzymania).
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐☆☆☆ (7/10) — mocne przy wielokrotnych biegach, ale to osobny projekt.
**Test tablicy prawdy:** ✅ (ale zakres duży)

### 💡 B4: Szybszy decode/merge audio (już częściowo zrobione — soundfile zamiast ffmpeg-per-chunk)
**Opis:** Kod już ma optymalizację (soundfile decode ~215x szybszy). Rozszerzyć na resztę.
**Mechanizm:** Audit gdzie jeszcze spawn ffmpeg per-element → zamień na in-process.
**Mocne:** ffmpeg spawn to koszt. In-process szybsze.
**Słabe:** Punktowe, wymaga audytu.
**Ocena:** ⭐⭐⭐⭐⭐⭐☆☆☆☆ (6/10) — drobne zyski, ale realne.
**Test tablicy prawdy:** ✅

### 💡 B5: Równoległy refactor napisów (ASS→SRT, split) — I/O lekki
**Opis:** refactor_subtitles po plikach — zrównoleglić jak extract.
**Mechanizm:** ThreadPool.
**Mocne:** Proste, spójne z extract.
**Słabe:** To CPU lekki (<5% czasu wg profilu) — mały zysk.
**Ocena:** ⭐⭐⭐⭐⭐☆☆☆☆☆ (5/10) — mały udział w czasie, mały zysk.
**Test tablicy prawdy:** ✅

### 💡 B6: Skip etapów gdy nic do roboty (early-exit guards)
**Opis:** Jeśli folder pusty / brak plików do etapu → pomiń bez setupu.
**Mechanizm:** Guard clause na wejściu każdego etapu.
**Mocne:** Zero kosztu na pustych etapach. Spójne z fixem pustych napisów.
**Ocena:** ⭐⭐⭐⭐⭐⭐☆☆☆☆ (6/10) — tania higiena, drobny zysk.
**Test tablicy prawdy:** ✅

### 🎲 GRUPA C: Eksperymentalne

### 💡 C1: Prefetch — ekstrakcja następnego odcinka podczas audio bieżącego
**Opis:** Wariant pipelineingu ograniczony do 1 kroku wyprzedzenia.
**Ocena:** ⭐⭐⭐⭐⭐⭐☆☆☆☆ (6/10) — podzbiór A1/A2.

### 💡 C2: Trwały log czasów per bieg (benchmark history)
**Opis:** Zapisuj czasy per-etap do pliku, żeby widzieć trend i regresje.
**Ocena:** ⭐⭐⭐⭐⭐☆☆☆☆☆ (5/10) — diagnostyka, nie zysk bezpośredni.

---

## 📊 Matryca Porównawcza (główne kandydaty)

| Kryterium | Waga | A1 Pipeline | A2 Uproszcz. | A4 Batch | B1 Cache extract |
|-----------|------|-------------|--------------|----------|------------------|
| ROI / zysk czasu | 30% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ | ⭐⭐⭐⭐⭐☆☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ |
| Ryzyko (niższe=lepiej) | 25% | ⭐⭐⭐⭐⭐☆☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ | ⭐⭐⭐⭐⭐⭐☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ |
| Wykonalność | 20% | ⭐⭐⭐⭐⭐⭐☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ |
| Zgodność z wizją usera | 25% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆☆☆☆☆☆ | ⭐⭐⭐⭐⭐⭐☆☆☆☆ |
| **SUMA WAŻONA** | 100% | **7.7** | **7.6** | **5.9** | **7.6** |

## 🧠 Strategie Decyzyjne

**Pareto 80/20:** B1 (cache extract, ~1 dzień) + A2 (uproszczony pipeline) dają większość
zysku za ułamek ryzyka A1. A1 pełny pipeline = ostatnie 20% zysku za 80% złożoności.

**Premortem — "za miesiąc padło, dlaczego?":**
- Pełny pipeline (A1) miał deadlock na kolejkach przy awarii jednego odcinka → cały auto zawisł.
  **Mitygacja:** twarde timeouty, izolacja per-item, testy z symulowaną awarią.
- Zrównoleglono za dużo audio (A4) → ElevenBytes zaczął zwracać 500/bany → wolniej niż
  sekwencyjnie. **Mitygacja:** NIE zwiększać współbieżności audio ponad obecne 85/odcinek;
  pipeline nakłada RÓŻNE etapy, nie mnoży audio.
- Brak pomiaru → optymalizowano nie ten potok. **Mitygacja:** pomiar per-etap PIERWSZY (już jest).

**Red Team na A1 (pełny pipeline):** "Co najgorszego?"
- Constraint #2 (izolacja błędów) trudny w kolejkach — jeśli potok audio rzuci wyjątek w
  `queue.get`, cały potok umiera. Trzeba try/except wokół KAŻDEGO item, nie wokół pętli.
- Przeplot logów zrobi kaszę w konsoli. Potrzebny prefix `[nazwa_odcinka]` w logach.
- Wniosek: A1 wykonalne, ale wymaga dyscypliny w 3 punktach (izolacja per-item, timeouty,
  logi z prefixem).

**First Principles:** Fundamentalnie zysk = suma czasów idle (czekanie na API) które można
wypełnić pracą. Jeśli translate+audio to ~60% czasu i ~70% z tego to idle sieci → teoretyczny
sufit zysku ~25-35% wall-clock. Realnie mniej (overhead, bariery). **Uczciwy szacunek: 15-30%.**

---

## 🔬 Deep Dive: Top 3

### 🔬 A2: Uproszczony pipeline (audio→merge w tle, potem translate→audio)
**Plan implementacji:**
1. Foldery per-odcinek: `temp/<mkv_stem>/{main_subs,alt_subs,temp}`. Wstrzyknięcie ścieżek do
   konstruktorów klas (pola dataclass już istnieją).
2. Napraw nazwy generyczne (`temp.wav`, `pp_speed_*`) → per-odcinek folder to załatwia.
3. Cache elevenbytes → per-odcinek podfolder (klucz zostaje indeks, ale w folderze odcinka).
4. `merge_tts_audio` → operuje na podfolderze konkretnego odcinka (dostaje nazwę/ścieżkę).
5. Orkiestracja: główna pętla iteruje odcinki przez etapy; merge każdego → `executor.submit`
   (tło); bariera `as_completed` na końcu.
**Zależności:** foldery per-odcinek MUSZĄ być pierwsze (fundament).
**Problemy i mitygacja:**
| Problem | Prawd. | Wpływ | Mitygacja |
|---------|--------|-------|-----------|
| Kolizje generycznych nazw | WYS | KRYT | foldery per-odcinek (fundament) |
| merge w tle widzi cudze pliki | ŚR | KRYT | merge dostaje ścieżkę podfolderu odcinka |
| Błąd 1 odcinka | ŚR | ZNACZ | try/except per submit, log, continue |
**Metryki sukcesu:** wall-clock spada mierzalnie (pomiar per-etap); wszystkie odcinki
przetworzone; zero nadpisań; błąd 1 odcinka nie psuje reszty.

### 🔬 A1: Pełny pipeline (4 potoki + kolejki)
**Plan:** jak A2 + 4 osobne workery-potoki połączone `queue.Queue`. Extract, translate, audio,
merge żyją równolegle. Sentinel (None) kończy potok.
**Zależności:** foldery per-odcinek + izolacja błędów per-item + logi z prefixem.
**Problemy:**
| Problem | Prawd. | Wpływ | Mitygacja |
|---------|--------|-------|-----------|
| Deadlock kolejek | ŚR | KRYT | maxsize rozsądny, timeouty, sentinel |
| Wyjątek zabija potok | WYS | KRYT | try/except wokół process(item), nie pętli |
| Debug trudny | WYS | ZNACZ | logi z prefixem odcinka, pomiar per-potok |
**Metryki:** jak A2 + każdy potok loguje throughput.

### 🔬 B1: Cache ekstrakcji między biegami
**Plan:** przed mkvextract sprawdź czy `temp/.../{stem}.aac` istnieje i rozmiar > próg → skip.
**Zależności:** żadne (samodzielne, można zrobić od ręki).
**Metryki:** drugi bieg tego samego wsadu pomija extract → mierzalnie szybszy start.

---

## ✅❌ Podział Kontekstowy

### ✅ DOBRE w tym kontekście
| # | Co | Dlaczego | Warunek |
|---|----|----------|---------|
| 1 | Foldery per-odcinek | Fundament pod wszystko, usuwa kolizje | poprawne wstrzyknięcie ścieżek |
| 2 | A2 uproszczony pipeline | Nakłada etapy, umiarkowane ryzyko | foldery per-odcinek najpierw |
| 3 | B1 cache extract | Tani zysk przy wielokrotnych biegach | walidacja rozmiaru |
| 4 | Pomiar per-etap (już jest) | Kieruje optymalizacją danymi | odpalić raz |

### ❌ ZŁE w tym kontekście
| # | Co | Dlaczego | Kiedy by zadziałało |
|---|----|----------|---------------------|
| 1 | B2 współbieżne tłumaczenie chunków | Google rate limit → 429/ban | gdyby własny serwer translate |
| 2 | A4 batch audio (3 odc × 85 req) | 255 req naraz → ElevenBytes 500 | gdyby stabilny serwer TTS |
| 3 | A3 asyncio full rewrite | Kod jest sync/thread, ryzyko #8 | gdyby pisane od zera |

### ⚠️ Zależy od kontekstu
| # | Co | Kiedy dobre | Kiedy złe |
|---|----|-------------|-----------|
| 1 | A1 pełny pipeline | Jeśli profil pokaże duże idle we wszystkich etapach | Jeśli 1 etap dominuje (wtedy A2 wystarczy) |
| 2 | B3 persistent audio cache | Dużo powtórek/biegów | Jednorazowe wsady |

---

## 🏆 REKOMENDACJA FINALNA

### Wybór: **Sekwencja etapowa** — fundament → A2 → (opcjonalnie A1), + B1 jako tani quick-win
**Ocena końcowa:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10 jako roadmapa)

**Kolejność wdrożenia:**
1. **B1 (cache extract)** — najtańszy zysk, zero ryzyka, natychmiast. Osobny, mały.
2. **Fundament: foldery per-odcinek** — bez tego nic z pipeliningu nie jest bezpieczne
   (constraint #4). Największa część pracy, ale czysto mechaniczna (wstrzyknięcie ścieżek).
3. **A2 (uproszczony pipeline)** — merge w tle, potem nakładanie translate/audio. Weryfikacja.
4. **A1 (pełne 4 potoki)** — TYLKO jeśli pomiar po A2 pokaże, że warto docisnąć.

### Dlaczego ten zestaw?
- Zgodny z wizją usera (potoki nakładane) ale wdrażany **etapami z weryfikacją** (constraint
  #2 wymaga ostrożności — izolacja błędów łatwiej testowana krok po kroku).
- Foldery per-odcinek to fundament, którego i tak nie da się ominąć.
- B1 daje natychmiastowy zysk niezależnie od reszty.

### Dlaczego NIE pozostałe?
- **A4 batch / B2 chunki** — łamią constraint #1 (limit API).
- **A3 asyncio** — ryzyko #8 (przepisanie sync/thread na async psuje istniejący retry/cache).

### Plan B
Jeśli foldery per-odcinek okażą się zbyt inwazyjne (regresje) → cofnąć się do A4-lite: batch
2 odcinki naraz TYLKO w extract+refactor (etapy bez limitu API), audio/translate sekwencyjnie.
Mniejszy zysk, ale mniejsze ryzyko.

### Uczciwy sufit zysku
First-principles szacunek: **15-30% wall-clock** (z ~5:02 → ~3:30-4:15). Nie więcej — limit
API to twarda granica. Kto obiecuje 2× szybciej, kłamie.

---

## 🔑 Kluczowe wnioski dla implementacji

1. **Pomiar PIERWSZY** — odpal raz z `_timed_stage`, potwierdź profil. Bez tego lecimy na
   hipotezie.
2. **Foldery per-odcinek to fundament** — wszystko inne zależy od tego.
3. **Izolacja błędów per-item** (nie per-potok) — try/except wokół przetwarzania POJEDYNCZEGO
   odcinka, nie wokół pętli potoku.
4. **Logi z prefixem `[nazwa_odcinka]`** — inaczej przeplot = kasza.
5. **Nie zwiększać współbieżności audio** — pipeline nakłada RÓŻNE etapy, nie mnoży requestów
   do tego samego API.
6. **Wdrażać etapami, każdy zweryfikowany** — to zmiana krytycznej ścieżki.
