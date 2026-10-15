# spec: przebudowa mm_avh od zera — terminalowa aplikacja anime

> data: 2026-07-12 | tryb: greenfield (nowy branch, wszystko od nowa)
> zebrane w brainstormingu z userem | materiał: audyt 00-06 + binarki 07 + echoreader 08 + tui 09
> status: DO ZATWIERDZENIA przez usera przed planem Sola

---

## 🎯 wizja w jednym zdaniu

Terminalowa aplikacja do anime — "coś pomiędzy Claude Code, terminalem a aplikacją webową, ale w terminalu" — która przetwarza pliki wideo (ekstrakcja napisów → refaktor → tłumaczenie → lektor TTS → złożenie) sterowana komendami `/slash` z autocomplete i rich-textowym panelem ustawień.

## 📐 tablica prawdy (twarde zasady — nienaruszalne)

| # | zasada | źródło |
|---|--------|--------|
| 1 | `utils/` NIETYKALNE — rdzeń usera (number_in_words, text_chunker...), użyty w całości, można rozbudować o funkcje, NIE przepisywać | user |
| 2 | minimalne komentarze — zero szumu, tylko nieoczywiste | user + pamięć |
| 3 | sync-first, async/wątki TYLKO gdzie realna równoległość przyspiesza (ekstrakcja, batch TTS) | user |
| 4 | type hints wszędzie + dataclass slots; stary typing (Dict/List/Optional) w kodzie który piszemy | user |
| 5 | prostota i szybkość > liczba plików; ale długoterminowo styl MangaShift (rejestry) wygrywa i user to akceptuje | user |
| 6 | rejestr silników (engine_id→klasa) tam gdzie WYBÓR: TTS + tłumaczenie. Heurystyka/render = nie rejestr | user |
| 7 | cały pipeline + wszystkie działające silniki + dedup/czyszczenie ZACHOWANE funkcjonalnie | user |
| 8 | Windows teraz, Linux-ready (bez hardkodów ścieżek, wykrywanie OS) | user |

## 🏗️ architektura docelowa

### warstwy (styl MangaShift, ale odchudzony pod terminalówkę)
- **rejestr silników** dla TTS i tłumaczenia: `services/<domena>/engines/` — engine_id→klasa, lazy import, zero if-ów per silnik. Rozwiązuje god-file `subtitle_to_speech.py` (1196 linii) i `tts_elevenbytes.py`.
- **domeny bez wyboru** (ekstrakcja MKV, merge, render ffmpeg) = zwykły moduł, bez ceremonii rejestru.
- **cienka fasada** per domena: dostaje engine_id, odpala z rejestru.
- **pipeline** = liniowy przebieg wołający fasady (NIE generyczny DAG jak MangaShift — przerost).
- **bootstrap()** = jedno miejsce składania zależności (config + wykryte ścieżki).
- **panel/CLI** = warstwa interakcji (banner, /komendy, /settings).

### co ŚWIADOMIE pomijamy (przerost MangaShift potwierdzony przez audyt 06)
- runtime/vram (refcount, VRAM pooling) → sekwencyjne ładowanie, wystarczy `with`
- runtime/llama (serwer LLM)
- rejestr modeli / catalog / downloader (HuggingFace) → mm_avh NIE ma modeli AI teraz (może w przyszłości = wtedy ciężki program)
- db/api/worker/frontend/events → terminalówka, nie serwer
- async-jako-domyślny-styl → sync-first

## 🔌 silniki i binarki

### rejestr TTS (główny ból → registry)
- **główny: ElevenBytes (ElevenLabs) v2 + v3** — dziś aktywny
- edge-tts (przenośny, Linux-ready), google
- balcon/SAPI → "do lamusa" (Windows-only, przestarzały IVONA) — zachować w rejestrze jako opcja, NIE testować teraz
- wzór kodu: EchoReader (ElevenLabs SDK, voice_settings, zarządzanie kluczem) wpięty w rejestr stylu MangaShift. Dodać retry/backoff na 429/5xx.

### rejestr tłumaczenia
- Google, DeepL API, GPT/AI — działające zachować
- DeepL-desktop → martwy (bug w audycie), olać
- dedup tłumaczeń (1000× to samo → 1×) + czyszczenie ASS znaczników — ZACHOWAĆ

### binarki (.exe) — badanie 07
- **MKVToolNix (mkvextract/mkvmerge) = MUSI zostać .exe** — brak dojrzałego zamiennika Python. Jest na Linux natywnie (Linux-ready OK).
- **ffmpeg = MUSI zostać .exe** — render wideo + wypalanie napisów (PyAV nie pokryje libx264/burn). Jest wszędzie.
- **espeak-ng, mkvinfo, mkvpropedit = MARTWY KOD** (tylko ścieżki) → usunąć
- **stylish_tts (567MB) = USUNĄĆ całkowicie** (martwy model)
- dystrybucja binarek: OTWARTE — pobieranie przy starcie (jak MangaShift external/ + hash) vs repo/release. Sol rozstrzygnie. Dziś: 218 plików bin/ źle trackowanych mimo .gitignore → naprawić.

## 🖥️ interfejs (serce wizji)

### zachowanie
1. odpalasz → **fajny ASCII banner**
2. **Enter → automatyczne przetworzenie całego folderu** (zero pytań)
3. **`/settings`** → panel ustawień, rich text, auto-zapis
4. **`/help`, `/auto`, `/manual`** → komendy
5. **autocomplete składni jak w Claude Code** (podpowiadanie gdy wpisujesz `/`)
6. tryb auto/manual przełączany i w /settings, i komendą

### stack UI — DECYZJA SOLA (badanie 09)
- fakt: Claude Code/Gemini CLI = JS/Ink (React w terminalu) — NIE do przeniesienia 1:1 w Pythonie
- rekomendacja badania: **prompt_toolkit (/slash + inline autocomplete + historia) + rich (banner/panele/kolory/progress)**
- alternatywa: textual (pełny framework, ale palette na Ctrl+P nie inline /, cięższy)
- **Sol decyduje ostatecznie**, ale MUSI uwzględnić: user MA gotowy pakiet kolorów/styli w rich (utils/rich_console z MangaShift — 150+ styli, ProgressBarManager, auto-highlight) i chce to wykorzystać

### ustawienia + klucze — DECYZJA SOLA (coś prostego, apka na 1 usera)
- config: JSON+panel vs pydantic-settings — Sol dobierze proste
- klucze API: .env vs szyfrowane — Sol dobierze proste (nie przekombinować)
- dziś: settings.py (684 linie god-file) + settings.json (gołe klucze) → rozbić/uprościć

## 📁 struktura folderów (do zaprojektowania przez Sola)

Wzór z MangaShift (badanie 06), zaadaptowany:
- kod źródłowy w pakiecie (services/, cli/, config/, setup/, utils/)
- `external/` wzór → `bin/` (binarki poza kodem, ew. pobierane)
- `workspace/` wzór → `working_space/` (dane robocze, gitignored, dziś zaśmiecone: luźne MKV/srt, kod convert_eac3_to_mp3.py wśród danych, .lnk, desktop.ini)
- `scripts/` wzór → uporządkować dzisiejszy chaos temp/ (217 plików: realne skrypty + jednorazowe dane ML wymieszane, wszystko gitignored)
- lekki `setup/doctor.py` (5-8 checków: ffmpeg? mkvtoolnix? klucze?) — wartościowe przy brakujących narzędziach

## 🧩 domeny pipeline (od usera)
wydobywanie · rafinacja (refaktor) · tłumaczenie · lektor (TTS) · składnia · porcje · renderowanie

## ⏳ odłożone na później
- **heurystyka wyboru stylu** (style_classifier) — user zbiera więcej przykładów testowych. Zostawić hak/miejsce, NIE przepisywać teraz.
- modele AI / lokalne (whisper, LLM, stylish powrót) — nie ma teraz, otwarte na przyszłość (ale wtedy = ciężki program)
- balcon→pyttsx3 migracja — wymaga testu jakości na głosach SAPI, nie teraz

---

## 🔍 MOJE OBSERWACJE (Claude — do rozważenia przez usera/Sola)

1. **Napięcie prostota vs registry — rozwiązane dobrze.** User waha się między god-file a MangaShift. Właściwa odpowiedź (i user do niej doszedł): registry TYLKO tam gdzie wiele silników (TTS, tłumacz), reszta płaska. To nie "całe MangaShift", to jego najlepszy 1 wzorzec bez przerostu.

2. **Największa wartość = rozbicie 2 god-files.** subtitle_to_speech.py (1196) i tts_elevenbytes.py (617) to 1810 linii bólu z if-ami per silnik. Rejestr TTS to rozwiązuje wprost. To powinien być PIERWSZY etap planu — najwięcej zysku.

3. **Panel /slash to najbardziej ryzykowna/nowa część.** Reszta (pipeline) to przepisanie działającego kodu w lepszej strukturze. Panel to NOWA funkcjonalność — warto go zrobić jako osobny, wcześnie testowalny moduł, nie na końcu.

4. **Uwaga na scope creep.** "Wszystko od zera" + panel + registry + cross-platform + sprzątanie to DUŻO. Sugeruję Solowi ETAPY: (1) szkielet+utils+config+panel-minimal, (2) rejestr TTS, (3) pipeline domeny, (4) tłumaczenie+dedup, (5) sprzątanie repo. Każdy etap = działająca apka.

5. **Cross-platform to realny nowy wymóg, nie kosmetyka.** balcon jest Windows-only. Jeśli Linux-ready serio — TTS domyślny na Linux musi być edge/piper. Rejestr to ogarnia (per-OS), ale trzeba to zaprojektować od początku, nie doklejać.

6. **working_space/temp/bin to bałagan do rozstrzygnięcia OSOBNO.** 567MB stylish + 218 plików bin/ w gicie + kod wśród danych. To sprzątanie git/dysku, nie architektura — nie mieszać z przebudową kodu, osobny etap.

7. **utils/ już częściowo znamy** — była wcześniej rozważana migracja rich_console/logger z MangaShift. To się teraz naturalnie wpina (Twój pakiet kolorów dla panelu). Ale zasada: utils to Twój kod, dokładamy do niego, nie przepisujemy.

8. **Ryzyko "nowego które nie robi tego co stare".** Greenfield kusi żeby zgubić edge-case'y. Twardy wymóg: nowy kod ma przejść ten sam happy-path co dziś na realnym MKV. Warto mieć 1 plik testowy MKV jako smoke-test po każdym etapie.
