# 📌 BRIEF: Tryb Auto dla MM_AVH

> Destylat pełnej ideacji → [`2026-06-28-tryb-auto.md`](./2026-06-28-tryb-auto.md) · Data: 2026-06-28

## 🎯 tl;dr

Ból usera = **ILOŚĆ decyzji** (~300 kliknięć / 40 odcinków), nie ich trudność. Problem dzieli się na 4 części: **(A)** wybór ścieżki audio, **(B)** wybór właściwej ścieżki napisów, **(C)** podział stylów dialog↔znaki, **(D)** bug `srt_to_ass`. **A i B to czysty odczyt metadanych MKV** (`language`, `track_name`, liczba linii) — zero AI. **C** to jedyna realna niepewność, mierzalna **sygnaturami formatu ASS** (rysunki `\p`, pozycje `\pos`, interpunkcja) — heurystyka, nie semantyka. **D** to bug inżynieryjny. Pipeline obliczeniowo już działa — brakuje tylko **warstwy decyzyjnej** nad nim.

## ✅ DECYZJA: LLM czy bez?

**BEZ LLM jako rdzeń.** Rekomendacja: **heurystyka deterministyczna offline** + **HITL** (pytanie do usera) jako siatka bezpieczeństwa przy niepewności + **LLM lokalny (Gemma) jako wyłączalny fallback dopiero w v2**. LLM API (Gemini/GPT) **odrzucony** w detekcji — łamie zasadę „działa bez internetu”.

**Dlaczego (3 argumenty, zbieżne z 4 strategii — First Principles/Premortem/Pareto/Red Team):**
1. Informacja o ścieżkach **już istnieje w metadanych** — to odczyt, nie zgadywanie. LLM = rozwiązanie nieistniejącego problemu.
2. Podział stylów jest **mierzalny formą, nie treścią**: hybryda nazwa+metryka (~96-98%, bo sygnały mają różne dziury) + profile grup (~99%). 
3. **~95% redukcji kliknięć** daje sama heurystyka+architektura (Pareto) — LLM nie tknąłby głównej bolączki bardziej.

Każda święta zasada (TP-1 brak-LLM, TP-2 offline, TP-3 HITL-tylko-przy-niepewności, TP-4 tryb-ręczny) spełniona przez rdzeń ✅.

## 🛠️ ZADANIA wg priorytetu

### 🔴 Krytyczne (MVP — rdzeń trybu auto)
- **[KROK 0] Flaga `auto_mode`** w `data/settings.py` (dataclass `slots=True` → dodać pole + w `load_from_file`/`change_settings_save_to_file`; default `False` = wstecznie kompatybilne, tryb ręczny zostaje — TP-4). Dodać też `auto_audio_lang_priority`, `auto_subs_lang_priority`, `auto_dialog_conf_threshold`.
- **[KROK 1 · Filar 1] Auto-selekcja ścieżek** (P8+P10): rozszerzyć `mkvtoolnix.py::_parse_track_data` o `track_name`/`forced`/`default`/liczbę linii (dziś czyta tylko `language`); dodać `select_audio_track`/`select_subtitle_track`; **rozdzielić selekcję od egzekucji** w `mkv_extract_track` (dziś splecione w pętli `input()`). Wybór napisów: pol>eng>pierwsza; przy remisie języka → ścieżka z większą liczbą linii, odrzuć `track_name ~ /sign|song/i`.
- **[KROK 2 · Filar 2] Auto-podział stylów** (P3+P7): ekstraktor metryk per styl (pos%, draw%, punct%, avg_len, line_count); klasyfikator hybrydowy nazwa+metryka z **confidence**; override `draw%>30 → ZNAK`; konflikt nazwa↔metryka → metryka wygrywa, ale obniż pewność. Podmienić ręczny `_select_styles` w `split_ass` na scoring. `conf<próg` → kolejka HITL.
- **[KROK 3 · Filar 3] Orkiestrator wsadowy** (P12+P13): branch `auto_mode` w `main()`; `run_auto_pipeline` (faza detekcji → zbiorczy HITL → **dry-run** → egzekucja per plik w `try/except` → raport); **wymusić auto-backend translacji** (Google/DeepL API) — inaczej `translate_gemini`/`chat_gpt` zawieszą batch na `getch()`.
- **[D] FIX `srt_to_ass`** (P15): zamienić mapowanie po `srt_index` (desync przy `continue`, linie 399–411) na **mapowanie po czasie startu** `event.start`; zachować tagi przez `re.split(r'({[^}]*})')`; brak dopasowania → zostaw oryginał. (Niezależne — można robić równolegle / pierwsze.)

### 🟡 Ważne (jakość, bezpieczeństwo)
- **Sanity-check napisów**: ścieżka „dialogu” z <50 liniami → podejrzane → HITL (chroni przed wyborem signs jako głównych).
- **Reguła anty-„cichy lektor”**: ZNAK wymaga *pozytywnego* sygnału (pos/draw), nie samego braku interpunkcji; karaoke `\k` → ZNAK.
- **Reguła OP/ED/piosenki** (uwaga usera): tekst piosenki bywa długi i z interpunkcją → bez dodatkowego sygnału heurystyka wzięłaby go za dialog. Karaoke `\k` (czas sylab) → twardo ZNAK, niezależnie od długości/nazwy. Nazwy `op/ed/song/lyric/insert/opening/ending` → sygnał ZNAK (wspierający, nie rozstrzygający sam). Zweryfikowane: liczba linii to najmocniejszy sygnał (Main=294/Default=284 → dialog; Signs=20/Next_Episode=1 → znak).
- **Log decyzji** (audytowalność: czemu styl→dialog/znak, z metrykami) + dry-run jako „test na żywych danych”.
- **Walidacja nazwy backendu** translatora (mapowanie po stringu jest kruche).

### 🟢 Nice-to-have (v2 — „turbo”)
- **Profile per-grupa-wydawnicza** (P11): rozpoznaj `[Erai-raws]` → gotowy układ; samouczenie ze słownika (nie ML → zgodne z TP-1).
- **Cache decyzji** (P14): `auto_decisions.json` — z czasem mniej pytań, idempotencja, zasila profile.
- **Fallback LLM lokalny** (P5, Gemma GGUF z EchoReadera): przy `conf<próg ∧ auto_llm_fallback`, domyślnie **OFF**, offline. Alternatywa dla HITL dla usera, który nie chce nawet zbiorczego pytania.

## ⚠️ RYZYKA (z mitygacją)
- 🔴 **„Cichy lektor”** (styl `Sign`=dialog → alt_subs, brak audio): metryka>nazwa przy konflikcie + dry-run pokazujący podział + log.
- 🔴 **Auto utyka na `getch()`** (translator manualny): wymuś auto-backend w trybie auto.
- 🟡 **Zła ścieżka napisów** (signs zamiast dialogu): liczba linii (P10) + sanity-check.
- 🟡 **Jeden zły plik wykoleja batch**: `try/except` per plik + raport, kontynuuj resztę.
- 🟡 **Za dużo pytań HITL**: kalibracja progu na dry-run; profile grup tną pytania.
- 🟡 **`slots=True`**: nowe pole musi być w dataclass + wszędzie, gdzie `Settings(...)` konstruowane (inaczej `TypeError`).
- 🟢 **Regresja trybu ręcznego**: ręczny musi zostać bit-identyczny; auto = nakładka, nie zamiennik.

## ❓ OTWARTE PYTANIA do usera
1. **Które grupy wydawnicze** przetwarzasz najczęściej (Erai-raws, SubsPlease, inne)? → decyduje, czy profile grup (P11) robić od razu czy w v2.
2. **Ile pytań HITL tolerujesz?** „Zero, chyba że naprawdę trzeba” vs „wolę potwierdzać niepewne”? → ustawienie progu pewności.
3. **Dry-run domyślnie?** Pokazać plan (które ścieżki/style) i czekać na OK, czy „od razu rób bez pokazywania”?
4. **Fallback LLM lokalny w v1 czy v2?** Rekomendacja: HITL w v1, LLM lokalny (Gemma) dopiero w v2 jako opcja. Zgoda?
5. **Preferencje języków** — potwierdź domyślne: audio `[jpn, eng, ...]`, napisy `[pol, eng, pierwsza]`. Czy audio bywa inne niż JP na tyle często, by zmieniać priorytet?

## 🔎 Do weryfikacji technicznej (1 komenda / próbka)
- Czy `mkvmerge -J plik.mkv` zwraca **liczbę linii** napisów (`num_index_entries` lub podobne) dla ASS/SRT? Jeśli nie → P10 potrzebuje lekkiego parsu pliku (tani narzut). Sprawdzić na realnej próbce przed implementacją Filaru 1.
