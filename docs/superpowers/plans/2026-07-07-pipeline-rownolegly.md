# Pipeline równoległy trybu auto — Implementation Plan

> **For agentic workers:** plan wykonywany przez arbitra (główny agent) delegującego
> etapy subagentom. Każdy etap weryfikowany przed następnym. Branch:
> feature/pipeline-rownolegly (baza: 8ebcb76 — bezpieczny działający punkt).

**Goal:** Tryb auto przetwarza odcinki jako pipeline z kolejkami — gdy odcinek skończy
tłumaczenie main, jego audio startuje od razu (trafia do kolejki audio), a tłumaczenie
kolejnego odcinka leci równolegle. Max 3 odcinki naraz. Czysty log. Zero utraty audio.

**Architecture:** Fundament = foldery per-odcinek (`temp/<stem>/{main_subs,alt_subs}`),
które usuwają 5 barier współdzielonego stanu (potwierdzone analizą przepływu). Dane już
płyną per-stem (stem = nazwa MKV bez `.mkv`, niezmiennik od ekstrakcji do output).
Orkiestrator: potok tłumaczenia → kolejka audio → potok audio, z izolacją błędów.

**Tech Stack:** Python 3.10+, ThreadPoolExecutor, queue.Queue, threading.Lock.

## Global Constraints (święte zasady usera)

- Max 3 odcinki równolegle (limit API ElevenBytes — 85 req/odcinek to granica, NIE zmieniać)
- NIE generować audio i tłumaczyć tego samego odcinka naraz (różne API, ale sekwencja per odcinek)
- Audio startuje ODRAZU po przetłumaczeniu main danego odcinka (nie czeka na inne)
- alt napisy — osobna kolej, po kolei (nie blokują audio main)
- Izolacja błędów: padnięcie 1 odcinka NIE przerywa pipeline ani innych odcinków
- Czysty log: output równoległych operacji nie może się przeplatać (atomowo pod lockiem)
- Komentarze w kodzie po angielsku; typing.List/Dict/Optional; guard clauses
- Tryb manualny BEZ zmian (interaktywny, batchowy jak dziś)
- Zero utraty/uszkodzenia audio (priorytet nad szybkością)

## Fundament z analizy przepływu (fakty)

- Wszystko parowane po STEM (mkvtoolnix.py:239 `filename[:-4]`), niezmiennik przez łańcuch.
- 6 etapów, każdy logicznie per-odcinek niezależny.
- 5 barier = współdzielone foldery + sekwencyjny main() + listdir w merge_tts_audio/process_output.
- Klasy (SubtitleToSpeech, SubtitleRefactor, MkvToolNix, MKVProcessing) mają pola-ścieżki
  dataclass → wstrzyknięcie per-odcinek przez konstruktor bez zmiany metod.

---

## ETAP 1: Czysty log równoległego wypakowywania

**Problem:** extract_tracks_from_mkv (start.py:90-137) — 6 wątków drukuje przez console.print
w mkv_extract_track/get_mkv_info → przeplot w kaszę.

**Rozwiązanie:** output każdego pliku zbierany i wypisywany atomowo pod wspólnym lockiem.
Ponieważ mkv_extract_track drukuje inline, najprościej: lock na sekcję drukującą per plik
(serializacja wypisywania, ekstrakcja wciąż równoległa — mkvextract to subprocess, drukowanie
to ułamek czasu).

**Deliverable:** log pokazuje czyste bloki (plik A cały, potem B cały), zero przeplatania.
Wypakowywanie wciąż równoległe (zysk zostaje).

**Weryfikacja:** test z symulacją — 2 wątki drukujące, sprawdź brak przeplotu.

---

## ETAP 2: Izolacja folderów per-odcinek (fundament)

**Rozwiązanie:**
1. `episode_temp_dirs(stem)` w constants.py → `{temp, main_subs, alt_subs}` pod `temp/<stem>/`.
2. Funkcja `ensure_episode_dirs(stem)` tworząca te foldery.
3. Wstrzyknięcie: gdziekolwiek tworzona jest instancja klasy dla odcinka w trybie auto,
   przekazać per-odcinek ścieżki do konstruktora.

**Deliverable:** każdy odcinek ma izolowany folder; klasy używają go przez wstrzyknięte pola.
merge_tts_audio/listdir widzi tylko pliki swojego odcinka → 5 barier znika.

**Weryfikacja:** test — dwa "odcinki" w osobnych folderach, brak kolizji nazw generycznych
(temp.wav, _elevenbytes_cache), merge jednego nie widzi plików drugiego.

---

## ETAP 3: Etapy per-odcinek

**Rozwiązanie:** wydzielić funkcje przetwarzające JEDEN odcinek przez dany etap, przyjmujące
stem + foldery per-odcinek:
- `extract_one_episode(mkv_filename, dirs)` — ekstrakcja do temp/<stem>/
- `refactor_one_episode(stem, dirs)` — ASS→SRT split w folderze odcinka
- `translate_one_main(stem, dirs, settings)` — tłumaczenie main
- `translate_one_alt(stem, dirs, settings)` — tłumaczenie alt (osobno)
- `audio_one_episode(stem, dirs, settings)` — audio + merge (izolowany, bez race)
- `output_one_episode(stem, settings)` — finalne scalenie

**Deliverable:** każdy etap wywoływalny per-odcinek, niezależnie.

**Weryfikacja:** test — jeden odcinek przez cały łańcuch w izolacji.

---

## ETAP 4: Orkiestrator pipeline z kolejkami

**Architektura (wizja usera):**
```
Potok TŁUMACZENIA (sekwencyjny, 1 odcinek naraz — limit API):
  dla każdego odcinka: extract → refactor → translate_main
    → gdy main gotowy: PUT do kolejki audio  (audio startuje!)
    → translate_alt (po kolei, nie blokuje audio)

Potok AUDIO (konsument kolejki, do 3 odcinków naraz? NIE — patrz niżej):
  bierze odcinek z kolejki → audio + merge → output
```

**Limit współbieżności:** max 3 odcinki "w locie" łącznie. Audio jednego odcinka = 85 req
API, więc realnie audio serializowane per odcinek (1-2 audio naraz max), ale NAKŁADA się na
tłumaczenie następnego. To jest sedno zysku: gdy audio odcinka A leci, tłumaczy się odcinek B.

**Izolacja błędów:** try/except wokół przetwarzania POJEDYNCZEGO odcinka. Padnięcie → log +
odcinek pominięty, pipeline żyje.

**Cleanup:** per-odcinek po jego zakończeniu (nie rmtree całości w trakcie).

**Deliverable:** tryb auto działa jako pipeline; audio nakłada się na tłumaczenie; max 3;
błąd izolowany; czysty log (prefix [stem]).

**Weryfikacja:** test symulacyjny — 5 odcinków, sprawdź że audio odcinka N nakłada się
czasowo na tłumaczenie N+1; błędny odcinek nie psuje reszty; wszystkie output powstają.

---

## Rola arbitra (główny agent)

Deleguję każdy etap subagentowi z precyzyjną specyfikacją. Po każdym:
1. Weryfikuję deliverable (py_compile, mypy, test).
2. Składam z resztą.
3. Commituję działający etap.
4. Dopiero wtedy następny etap.

Na końcu: pełna weryfikacja + oddanie userowi do testów na prawdziwych plikach.

## Ryzyka

| ryzyko | mitygacja |
|--------|-----------|
| Utrata audio (jak w cofniętym A2) | foldery per-odcinek — merge widzi tylko swój odcinek |
| Przeciążenie API (500/bany) | max 3 odcinki, audio nie mnoży req ponad 85/odcinek |
| Deadlock kolejek | sentinel, timeouty, bounded queue |
| Przeplot logów | prefix [stem] + atomowe wypisywanie pod lockiem |
| Cleanup kasuje żywe dane | cleanup per-odcinek po jego zakończeniu, nie rmtree całości |
