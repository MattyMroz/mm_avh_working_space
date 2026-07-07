# brief: architektura potokowa + zyski wydajności

> status: UZGODNIONE (kierunek) — 2026-07-07
> źródło: `2026-07-07-architektura-potokowa.md` | tryb: big

## tl;dr
Tryb auto przetwarza odcinki sekwencyjnie etap-po-etapie. Wizja usera: **potoki
(extract/translate/audio/merge) działają jednocześnie, odcinki płyną jak taśma** —
martwe czasy oczekiwania API jednego odcinka wypełnia praca innego. Nie łamie
limitów API (różne API nie konkurują). Uczciwy sufit zysku: **15-30% wall-clock**
(~5:02 → ~3:30-4:15), nie więcej — limit API to granica.

## decyzja
Wdrożenie **etapami** (nie wszystko naraz — to krytyczna ścieżka):
1. **B1 cache extract** — pomiń re-ekstrakcję gdy plik istnieje (tani, zero ryzyka)
2. **Fundament: foldery per-odcinek** — `temp/<mkv>/...`, bez tego pipelining =
   nadpisywanie plików (obawa usera). Klasy już mają pola-ścieżki → wstrzyknięcie.
3. **A2 uproszczony pipeline** — merge w tle + nakładanie translate/audio
4. **A1 pełne 4 potoki** — TYLKO jeśli pomiar po A2 pokaże że warto

## zadania
### 🔴 krytyczne
- [ ] **Pomiar per-etap odpalić** (już w kodzie) → **rezultat:** potwierdzony profil czasu, wiadomo który potok dominuje
- [ ] **Foldery per-odcinek:** `temp/<mkv_stem>/{main_subs,alt_subs,temp}`, wstrzyknąć ścieżki do SubtitleToSpeech/MkvToolNix/SubtitleRefactor/MKVProcessing → **rezultat:** izolacja, zero nadpisań
- [ ] **Naprawić generyczne nazwy** (temp.wav, pp_speed_*, _elevenbytes_cache) → per-odcinek → **rezultat:** brak kolizji
- [ ] **merge_tts_audio** operuje na podfolderze odcinka (nie listdir całości) → **rezultat:** sedno pipeliningu bezpieczne

### 🟡 wysokie
- [ ] **A2 pipeline:** merge w tle (executor.submit + bariera as_completed), izolacja błędów per-item, logi z prefixem [odcinek] → **rezultat:** nakładanie etapów
- [ ] **B1 cache extract:** guard path.exists+rozmiar przed mkvextract → **rezultat:** szybszy powtórny bieg

### 🟢 normalne (warunkowe)
- [ ] **A1 pełne potoki** — jeśli pomiar potwierdzi zysk
- [ ] **B4 audit ffmpeg-spawn** → in-process gdzie się da

## ryzyka
| ryzyko | trigger | akcja |
|--------|---------|-------|
| Nadpisywanie plików odcinków | wspólny folder + równoległość | foldery per-odcinek NAJPIERW |
| Błąd 1 odcinka zabija potok | wyjątek w pętli potoku | try/except per-item, nie per-pętla |
| Audio 500/ban | za dużo req naraz | NIE mnożyć req audio; nakładać różne etapy |
| Deadlock kolejek (A1) | zły maxsize | timeouty, sentinel, testy z awarią |
| Optymalizacja nie tego potoku | brak pomiaru | pomiar per-etap PIERWSZY |

## odrzucone (łamią limit API / zbyt ryzykowne)
- ❌ B2 współbieżne tłumaczenie chunków (Google 429/ban)
- ❌ A4 batch 3 odc × 85 req audio (ElevenBytes 500)
- ❌ A3 asyncio full rewrite (psuje istniejący sync/thread retry/cache)

## otwarte pytania
- ❓ Profil czasu — który potok realnie dominuje? (pomiar odpowie)
- ❓ Zacząć od B1 (tani quick-win) czy od razu fundament foldery per-odcinek?
