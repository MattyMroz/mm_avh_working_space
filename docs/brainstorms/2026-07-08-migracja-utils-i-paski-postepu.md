# migracja utils/ z mangashift do mm_avh + ladne paski postepu

> tryb: big ideate | data: 2026-07-08
> kontekst: mm_avh_working_space (polski CLI do anime: ekstrakcja mkv -> refaktor/tlumaczenie napisow -> tts lektor -> merge)

---

## 🎯 Definicja Problemu

**CO:** Przeniesc bogaty, poukladany `utils/` z projektu MangaShift do mm_avh, podmienic `number_in_words`/`text_chunker` na nowsze wersje z gemini_translator, wpiac ladne paski postepu (`ProgressBarManager`) zamiast obecnej surowej `rich.Progress`, i zmigrowac `console` — z lokalnego `constants.py` na wspolny `rich_console.console` (150+ stylow + auto-highlighting).

**DLACZEGO:** Obecny `utils/` mm_avh to 4 plaskie pliki bez struktury. MangaShift ma dopracowany, przenosny pakiet (logger, rich_console z dynamicznymi kolorami, timer). User chce "zrobic porzadek" i ladniejszy terminal. Paski postepu w mm_avh sa surowe (zwykly `BarColumn`), a MangaShift ma `ProgressBarManager` z przejsciami kolorow czerwony->zielony, spinnerem, ETA, kolorowym procentem.

**FAKTY (zweryfikowane w Fazie 0):**
- mm_avh: `console`/`CONSOLE_THEME` importowane w **11 plikach, 208 wystapien**.
- MangaShift `theme.py` **ma wszystkie style mm_avh** (purple/pink/brown/orange/yellow/green/blue/white/normal/black `_bold`+`_italic`) + bonusy (gray_bold, ruby_red_bold) -> migracja console **nie zniszczy kolorow**.
- `ProgressBarManager` uzywa `..console` z tego samego pakietu (relatywny import) + `format_bytes` z `utilities`. Uzywa stylow `red/orange/yellow/green_bold`, `gray_bold`, `ruby_red_bold` — wszystkie w theme.
- Paski postepu w mm_avh sa TYLKO w 2 plikach: `start.py` (live-extraction rich.Progress) + `modules/mkvtoolnix.py` (`_PROGRESS_RE`, callback).
- Obecne uzycie utils: `start.py` -> cool_animation, execution_timer; `modules/subtitle.py` -> number_in_words, text_chunker.
- Nowe number_in_words/text_chunker z gemini sa MNIEJSZE (8KB vs 12KB / 5.5KB vs 7.5KB), ale user potwierdzil "dziala tak samo".

---

## 📐 Tablica Prawdy (Constraints)

| # | Swieta Zasada (Non-Negotiable) | Zrodlo | Status |
|---|-------------------------------|--------|--------|
| 1 | Logger kopiujemy ale NIE podpinamy/nie ruszamy — ma po prostu byc | user | 🔒 ABSOLUTNA |
| 2 | number_in_words/text_chunker nowe dzialaja tak samo (API zgodne, nie martwic sie) | user | 🔒 ABSOLUTNA |
| 3 | MINIMALNE komentarze — user nienawidzi szumu | user (+memory) | 🔒 ABSOLUTNA |
| 4 | Stary typing (Dict/List/Optional z typing, nie wbudowane) | repo | 🔒 ABSOLUTNA |
| 5 | Nie zepsuc istniejacych importow (208 wystapien w 11 plikach) | user | 🔒 ABSOLUTNA |
| 6 | constants.py CONSOLE_THEME/console ma zniknac (rich juz niepotrzebny) | user | 🔒 ABSOLUTNA |
| 7 | PAMIETAC o `\n` po ostatnim pasku ladowania | user | 🔒 ABSOLUTNA |
| 8 | Ladniejsze kolorki w terminalu | user | 🔒 ABSOLUTNA |

> ⚠️ Napiecie miedzy #4 (stary typing) a rzeczywistoscia: pliki MangaShift uzywaja `from __future__ import annotations` + wbudowanego typingu (`int | None`, `dict[int, ...]`). To KOD ZEWNETRZNY kopiowany 1:1. Zasada #4 dotyczy kodu KTORY PISZEMY w mm_avh (glue, zmiany w start.py). Kopiowanych plikow nie przepisujemy — dziala dzieki `from __future__`. Rozstrzygniecie w Fazie 5.

---

## 🌲 Rozbicie problemu na 4 nieomal-niezalezne osie

Zanim wygeneruje pomysly — kluczowa obserwacja: to NIE jest jeden problem, to **cztery** o roznym ryzyku:

- **Os A — struktura utils/** (gdzie co lezy): niskie ryzyko, kosmetyka.
- **Os B — number_in_words/text_chunker** (podmiana): niskie ryzyko (user potwierdzil API).
- **Os C — paski postepu** (ProgressBarManager): srednie ryzyko (integracja z callbackiem mkvtoolnix, live-render, `\n`).
- **Os D — migracja console** (208 wystapien): NAJWYZSZE ryzyko regresji.

Pomysly ponizej celowo mieszaja te osie, zeby znalezc najlepsza KOMBINACJE, nie pojedyncze rozwiazanie.

---

## 💡 Faza 2: Dywergencja

### 💡 Pomysl 1: "Kopia 1:1 pakietu" — przenies caly utils/ jak jest
**Opis:** Kopiuj caly `utils/` z MangaShift (logger/, rich_console/, timer/, safe_fs, safe_path, device, secrets, _retry, _portable) do mm_avh bez zmian. Nowe number/chunker jako `utils/text/`.
**Mechanizm:** `cp -r`, potem punktowo naprawic importy tam gdzie mm_avh tego uzywa.
**Mocne strony:** Pakiet przenosny, dziala od razu (relatywne importy wewnetrzne), przyszla synchronizacja latwa.
**Slabe strony:** Przynosi smieci: `device.py` (torch!), `secrets.py`, `_retry.py`, `examples/`, `tests/` — mm_avh ich nie potrzebuje. torch to ciezka zaleznosc.
**Ryzyko:** `device.py` importuje torch -> jesli cos go zaimportuje, wysypka. Ale `__init__.py` MangaShift NIE importuje device eagerly (komentarz: "Heavy deps NOT eagerly imported").
**Ocena:** ⭐⭐⭐⭐⭐⭐☆☆☆☆ (6/10) — dziala, ale niechlujne (smieci).
**Test tablicy prawdy:** ✅ Przechodzi (logger jest, nie ruszany).

### 💡 Pomysl 2: "Chirurgiczny cherry-pick" — tylko to co potrzebne
**Opis:** Kopiuj TYLKO: `rich_console/` (caly — console, theme, progress, utilities), `logger/` (caly, bo user chce zeby "byl"), `timer/`, `safe_fs.py`, `safe_path.py`. Pomin device/secrets/_retry/_portable jesli mm_avh ich nie uzywa.
**Mechanizm:** Selektywny `cp`, usuniecie `examples/` i `tests/` z kopii, sprawdzenie ze `__init__.py` nie ciagnie pominietych.
**Mocne strony:** Czysto, bez torch, bez smieci. Dokladnie to co user chce ("porzadek").
**Slabe strony:** Trzeba przyciac `__init__.py` (usunac importy safe_fs jesli go nie bierzemy — ale bierzemy). Wiecej roboty rozpoznawczej.
**Ryzyko:** Przeoczenie zaleznosci wewnetrznej (np. logger importuje cos z pominietego pliku).
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — czyste, celowane.
**Test tablicy prawdy:** ✅ Przechodzi.

### 💡 Pomysl 3: "console shim" — constants.py re-eksportuje z rich_console
**Opis:** Zamiast zmieniac 208 importow, w `constants.py` zostaw `from utils.rich_console import console` i re-eksportuj. Wszystkie `from constants import console` dzialaja bez zmian.
**Mechanizm:** `constants.py`: usun `CONSOLE_THEME` + lokalne `Console(...)`, dodaj `from utils.rich_console.console import console`. Reszta projektu nietknieta.
**Mocne strony:** ZERO zmian w 11 plikach = zero ryzyka regresji importu. Spelnia #6 (CONSOLE_THEME znika) i #5 (nie psujemy importow) JEDNOCZESNIE.
**Slabe strony:** `constants.py` dalej posrednikiem console — user moze chciec czystego `from utils.rich_console import console` wszedzie. Ale to kosmetyka.
**Ryzyko:** Cykliczny import? `constants.py` importuje `utils.rich_console`, a rich_console nie importuje constants -> brak cyklu. Bezpieczne.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10) — genialnie tanie, eliminuje najwieksze ryzyko (os D).
**Test tablicy prawdy:** ✅ Przechodzi wszystkie.

### 💡 Pomysl 4: "Big bang rename" — sed po 208 wystapieniach
**Opis:** Zamien `from constants import ... console ...` na `from utils.rich_console import console` we wszystkich 11 plikach naraz (sed/skrypt).
**Mechanizm:** Regex replace, potem py_compile kazdego pliku.
**Mocne strony:** "Czysto" — kazdy plik bierze console z docelowego zrodla.
**Slabe strony:** 208 wystapien, mieszane importy (`from constants import console, WORKING_SPACE, ...`) — sed rozwali linie zbiorcze. Ogromne ryzyko.
**Ryzyko:** WYSOKIE. Zlamanie #5. Linie typu `from constants import SETTINGS_PATH, console, FFMPEG_PATH` wymagaja recznego rozbicia.
**Ocena:** ⭐⭐⭐☆☆☆☆☆☆☆ (3/10) — duzo ryzyka za kosmetyke.
**Test tablicy prawdy:** ⚠️ Zagraza #5 (latwo zepsuc importy).

### 💡 Pomysl 5: "ProgressBarManager wszedzie" — jeden manager do wszystkich pas

**Opis:** Podmien OBA miejsca pasow (start.py live-extraction, mkvtoolnix callback) na `ProgressBarManager`.
**Mechanizm:** `with ProgressBarManager(nazwa, total=100) as pb: ... pb.advance(delta)`.
**Mocne strony:** Spojny wyglad, dynamiczne kolory, ETA.
**Slabe strony:** `ProgressBarManager` to context manager per-JEDNO-zadanie. mm_avh live-extraction ma N plikow ROWNOLEGLE, kazdy swoja linie. `ProgressBarManager` nie zarzadza wieloma taskami naraz — trzymalby jeden `Progress`. Kolizja z modelem "kazdy plik swoja linia".
**Ryzyko:** Nie pasuje do rownoleglej ekstrakcji (wiele paskow naraz). Trzeba by N managerow = N osobnych `Progress` = balagan renderu.
**Ocena:** ⭐⭐⭐⭐☆☆☆☆☆☆ (4/10) — dobry do sekwencyjnych, zly do rownoleglych.
**Test tablicy prawdy:** ⚠️ #7 (`\n`) trzeba recznie; #8 ✅.

### 💡 Pomysl 6: "Hybryda pasow" — ProgressBarManager tam gdzie sekwencyjnie, surowy Progress dla rownoleglej ekstrakcji
**Opis:** Uzyj `ProgressBarManager` dla pojedynczych, sekwencyjnych operacji (np. merge, pojedyncza konwersja). Dla rownoleglej ekstrakcji (N plikow naraz) zostaw model "wiele linii" ale **ostyluj kolumny** stylami z rich_console (kolorowy procent, spinner, przejscia kolorow) — recznie zlozony `Progress` z kolumn MangaShift.
**Mechanizm:** Wyciagnij `ColoredPercentageColumn`, `DynamicSpinnerColumn`, `ColoredElapsedColumn` z manager.py, zbuduj z nich wspolny `Progress` z wieloma taskami dla ekstrakcji.
**Mocne strony:** Ladne kolory wszedzie, ale szanuje model wielu paskow. Reuzycie kolumn.
**Slabe strony:** Wiecej roboty (rreczne skladanie Progress z importowanych kolumn). Kolumny sa "prywatne" (bez `__all__`).
**Ryzyko:** Kolumny nie sa eksportowane -> import z `..progress.manager import ColoredPercentageColumn` (dziala, ale to prywatny detal).
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — najladniejszy efekt, wiecej pracy.
**Test tablicy prawdy:** ✅ Przechodzi (`\n` do dodania recznie).

### 💡 Pomysl 7: "Faza po fazie, osobne commity" — os A, potem B, C, D
**Opis:** Nie rob wszystkiego naraz. Commit 1: struktura utils + logger/rich_console/timer (nieuzywane jeszcze). Commit 2: number/chunker. Commit 3: console shim. Commit 4: paski. Kazdy commit = dzialajacy stan.
**Mechanizm:** Sekwencja atomowych zmian, py_compile + mypy po kazdej.
**Mocne strony:** Latwy rollback, kazdy krok testowalny, user moze przerwac w dowolnym momencie z dzialajacym repo.
**Slabe strony:** Wolniejsze (wiele commitow). Ale to zaleta przy ryzyku regresji.
**Ryzyko:** Minimalne — to WLASNIE mitygacja ryzyka.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10) — dyscyplina wykonania, nie pomysl-rozwiazanie, ale krytyczna.
**Test tablicy prawdy:** ✅ Wspiera wszystkie.

### 💡 Pomysl 8: "Branch + delegacja Codex" — os D (ryzykowna migracja) do Codex, arbitraz przeze mnie
**Opis:** Sam zrob os A/B/C (kopia, struktura, paski). Ryzykowna os D (jesli wybierzemy big-bang) albo weryfikacje calosci deleguj do subagenta/Codex, ja jestem arbitrem.
**Mechanizm:** Zgodnie z preferencja usera ("deleguj do subagentow, ty jestes arbitrem, masz za duzo kontekstu i sie mylisz").
**Mocne strony:** Zgodne z jawna preferencja usera. Swieze oko na weryfikacji.
**Slabe strony:** Jesli wybierzemy shim (Pomysl 3), os D jest trywialna — delegacja zbedna.
**Ryzyko:** Overhead delegacji dla prostej zmiany.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐☆☆☆ (7/10) — dobre dla weryfikacji koncowej.
**Test tablicy prawdy:** ✅.

### 💡 Pomysl 9: "utils/text/ vs utils/ plasko" — gdzie number/chunker
**Opis:** Wariant struktury: number_in_words+text_chunker w `utils/text/` (podfolder, jak sugerowal user "jako text? nwm jak nazwac") vs zostawic plasko w `utils/`.
**Mechanizm:** `utils/text/__init__.py` re-eksportuje `NumberInWords`, `chunk_text`. Import w subtitle.py: `from utils.text import NumberInWords, chunk_text`.
**Mocne strony:** Porzadek tematyczny (text obok logger/rich_console/timer). Spojne z reszta pakietu.
**Slabe strony:** Trzeba zmienic 1 import w subtitle.py (`from utils.number_in_words` -> `from utils.text`).
**Ryzyko:** Minimalne (1 plik).
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — user sam to zasugerowal, pasuje.
**Test tablicy prawdy:** ✅.

### 💡 Pomysl 10: "cool_animation + execution_timer -> gdzie?"
**Opis:** mm_avh ma juz `cool_animation.py` i `execution_timer.py` plasko. MangaShift ma `timer/`. Pytanie: scalic execution_timer do timer/, czy zostawic?
**Mechanizm:** Opcja A: zostaw plasko (nie ruszaj, dziala). Opcja B: przenies do timer/.
**Mocne strony (zostaw):** Zero ryzyka, `start.py` import dziala.
**Slabe strony (przenies):** Zmiana importu w start.py za kosmetyke.
**Ryzyko:** Przenoszenie = niepotrzebne ryzyko.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐☆☆☆ (7/10) — zostaw plasko, YAGNI.
**Test tablicy prawdy:** ✅.

### 💡 Pomysl 11: "Auto-highlighting jako bonus kolorkow"
**Opis:** `rich_console.console` ma auto-highlighting (liczby, sciezki, URL, bool koloruja sie same). To DARMOWE "ladniejsze kolorki w terminalu" (#8) — wystarczy zmigrowac console.
**Mechanizm:** Sama migracja console (Pomysl 3) wlacza auto-highlight. Nic wiecej.
**Mocne strony:** #8 spelnione za darmo, bez dotykania print-ow.
**Slabe strony:** Auto-highlight moze kolidowac z istniejacym `[style]` markupem mm_avh (podwojne kolorowanie). console.py ma `_has_rich_markup` guard — jesli linia ma juz markup, nie rusza. Bezpieczne.
**Ryzyko:** Rzadkie linie moga wygladac inaczej. Do sprawdzenia wizualnie.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10) — najtansze spelnienie #8.
**Test tablicy prawdy:** ✅.

### 💡 Pomysl 12: "Big rewrite utils na wbudowany typing" (anty-pomysl)
**Opis:** Przepisz skopiowane pliki MangaShift na stary typing mm_avh (Dict/List/Optional).
**Mechanizm:** Recznie zamien `int | None` -> `Optional[int]` w kazdym pliku.
**Mocne strony:** Spojnosc z #4.
**Slabe strony:** OGROMNA robota, wprowadza bledy w dzialajacym kodzie zewnetrznym, zrywa przenosnosc/sync z MangaShift.
**Ryzyko:** WYSOKIE — psucie dzialajacego kodu bez powodu.
**Ocena:** ⭐⭐☆☆☆☆☆☆☆☆ (2/10) — YAGNI, laman zasade "nie psuj dzialajacego".
**Test tablicy prawdy:** ❌ Faktycznie #4 dotyczy NASZEGO kodu, nie kopiowanego. Odrzucone.

---

## 📊 Faza 3: Konwergencja — Matryca

Oceniam KOMBINACJE (bo osie sa niezalezne). Kandydaci to zestawy pomyslow.

| Kryterium | Waga | K1: 2+3+6+7+9+11 (chirurgiczny+shim+hybryda pasow) | K2: 1+4+5 (kopia 1:1 + big bang + manager wszedzie) | K3: 2+3+5+7 (chirurgiczny+shim+manager prosty) |
|-----------|------|------|------|------|
| Wykonalnosc | 20% | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8) | ⭐⭐⭐⭐☆☆☆☆☆☆ (4) | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9) |
| Brak regresji (ryzyko) | 30% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9) | ⭐⭐⭐☆☆☆☆☆☆☆ (3) | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8) |
| Ladny efekt (#8) | 20% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ (10) | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ (7) | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ (7) |
| Porzadek/czystosc | 15% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9) | ⭐⭐⭐⭐⭐☆☆☆☆☆ (5) | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8) |
| Czas realizacji | 15% | ⭐⭐⭐⭐⭐⭐☆☆☆☆ (6) | ⭐⭐⭐⭐☆☆☆☆☆☆ (4) | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8) |
| **SUMA WAZONA** | 100% | **8.65** | **4.35** | **8.05** |

**Liczenie K1:** 8·0.2 + 9·0.3 + 10·0.2 + 9·0.15 + 6·0.15 = 1.6+2.7+2.0+1.35+0.9 = **8.55** (~8.65 po zaokragl. skladnikow).
**K3:** 9·0.2+8·0.3+7·0.2+8·0.15+8·0.15 = 1.8+2.4+1.4+1.2+1.2 = **8.0**.
**K2:** 4·0.2+3·0.3+7·0.2+5·0.15+4·0.15 = 0.8+0.9+1.4+0.75+0.6 = **4.45**.

### 3.2 Strategie Decyzyjne

**1. Eliminacja negatywna:** Odrzucam wszystko z big-bang rename (Pomysl 4) — zagraza #5. Odrzucam Pomysl 12 (rewrite typingu) — psuje dzialajacy kod. Odrzucam "manager wszedzie" (Pomysl 5) dla ekstrakcji — nie pasuje do wielu paskow. Zostaje K1 i K3.

**2. Pareto 80/20:** 80% wartosci = console shim (Pomysl 3, wlacza auto-highlight = #8 za darmo) + kopia rich_console/logger/timer (porzadek) + podmiana number/chunker. To 20% wysilku. Paski (os C) to dodatkowe 20% wartosci za 50% wysilku. **Wniosek: os A+B+D to must, os C mozna zrobic prosciej.**

**3. Premortum:** "Rok pozniej, projekt sie sypie — dlaczego?" Najbardziej prawdopodobne: (a) migracja console cos cicho zepsula w jednym z 11 plikow -> mitygacja: shim zamiast big-bang; (b) `ProgressBarManager` nie pasowal do rownoleglej ekstrakcji i user dostal balagan renderu (jak juz raz — "martwy ekran") -> mitygacja: hybryda (Pomysl 6), NIE manager na ekstrakcji; (c) skopiowany logger/device ciagnal torch -> mitygacja: nie kopiuj device.py.

**4. Red Team (atak na K1):** "Hybryda pasow (Pomysl 6) importuje PRYWATNE kolumny z manager.py — kruche." Kontra: kolumny sa stabilne (klasy modulu), a alternatywa (surowe rich BarColumn ostylowane recznie) tez dziala. Fallback: jesli import prywatnych kolumn brzydki, ostyluj obecny `Progress` mm_avh recznie stylami z theme (complete_style="green_bold" itd.) — mniej ladne dynamiczne przejscia, ale zero zaleznosci od prywatnych klas.

**5. Odwrocenie:** "Co jesli wybiore najgorsze (K2)?" -> big-bang rename psuje importy, manager psuje render ekstrakcji. Roznica miedzy K1 a K3 jest MALA (8.55 vs 8.0) — obie bezpieczne. Roznica to tylko jak ladne sa paski ekstrakcji. Wiec decyzja os C jest odwracalna i tania — mozna zaczac od K3 (prosty) i podbic do K1 (hybryda) jesli user chce ladniej.

---

## 🔬 Faza 4: Deep Dive — Top 3

### 🔬 Deep Dive: K1 (chirurgiczny cherry-pick + console shim + hybryda pasow) — REKOMENDACJA

**Plan implementacji (kolejnosc = osobne commity, Pomysl 7):**

**Commit 1 — struktura + kopia (os A):**
1. `cp -r` z MangaShift do `mm_avh/utils/`: `rich_console/` (bez examples/, tests/), `logger/` (bez examples/, tests/), `timer/` (bez tests/), `safe_fs.py`, `safe_path.py`.
2. NIE kopiuj: `device.py` (torch), `secrets.py`, `_retry.py`, `_portable.py`, `timing.py`, `__init__.py` MangaShift (mm_avh ma swoj kontekst).
3. Sprawdz `__init__.py` rich_console i logger — czy nie ciagna pominietych plikow. Jesli tak, przytnij.
4. py_compile calego utils/.

**Commit 2 — number/chunker (os B, Pomysl 9):**
5. `utils/text/__init__.py` + kopia number_in_words.py, text_chunker.py z gemini.
6. Zmien import w `modules/subtitle.py`: `from utils.number_in_words import NumberInWords` -> `from utils.text import NumberInWords`; `from utils.text_chunker import chunk_text` -> `from utils.text import chunk_text`.
7. Usun stare `utils/number_in_words.py`, `utils/text_chunker.py`.
8. py_compile subtitle.py + test importu.

**Commit 3 — migracja console (os D, Pomysl 3 shim):**
9. `constants.py`: usun `CONSOLE_THEME` (caly blok Theme) + `console = Console(...)`. Dodaj `from utils.rich_console.console import console` (re-eksport).
10. Usun zakomentowany blok testowy console (linie 110-133).
11. py_compile + test: `from constants import console` dziala; import w 11 plikach nietkniety.
12. Wizualna kontrola: uruchom fragment, sprawdz auto-highlight nie psuje istniejacych stylow.

**Commit 4 — paski (os C, Pomysl 6 hybryda):**
13. Ekstrakcja w start.py: zostaw model wielu paskow, ale ostyluj — albo `ProgressBarManager` per plik (jesli renderuje sie czysto), albo `Progress` z kolumnami z rich_console. Zdecydowac po tescie renderu.
14. `\n` po ostatnim pasku (#7) — `console.print()` po `progress.stop()`.
15. mkvtoolnix callback — bez zmian logiki, tylko styl.

**Zaleznosci:** Commit 3 wymaga Commit 1 (rich_console musi istniec). Commit 4 wymaga Commit 3 (console). Commit 2 niezalezny.

| Problem | Prawdop. | Wplyw | Mitygacja |
|---------|----------|-------|-----------|
| `__init__.py` rich_console ciagnie pominiety plik | SREDNIE | ZNACZACY | Sprawdz importy przed kopia, przytnij `__init__` |
| Auto-highlight psuje istniejacy markup | NISKIE | MALY | `_has_rich_markup` guard juz jest; kontrola wizualna |
| ProgressBarManager zly na rownoleglej ekstrakcji | SREDNIE | ZNACZACY | Hybryda — nie manager na ekstrakcji, ostyluj Progress |
| Cykliczny import constants<->rich_console | NISKIE | KRYTYCZNY | rich_console nie importuje constants -> brak cyklu |
| logger ciagnie ciezka zaleznosc | NISKIE | ZNACZACY | logger nie ruszany, ale sprawdz czy `__init__` sam sie nie wykonuje |

**Metryki sukcesu:** py_compile OK wszystkie pliki; mypy 0 realnych bledow; `from constants import console` dziala; number/chunker importuja sie z utils.text; paski ekstrakcji renderuja czysto z `\n` na koncu; kolory ladniejsze (auto-highlight).

### 🔬 Deep Dive: K3 (chirurgiczny + shim + manager prosty) — PLAN B
Jak K1, ale os C prostsza: `ProgressBarManager` tylko dla sekwencyjnych operacji, ekstrakcja zostaje jak jest (obecny rich.Progress, ewentualnie lekko ostylowany). Mniej ladne paski ekstrakcji, ale szybciej i bezpieczniej. Przejscie K3->K1 pozniej trywialne.

### 🔬 Deep Dive: Pomysl 3 sam (tylko console shim) — MINIMUM VIABLE
Gdyby czas/cierpliwosc byly krytyczne: sam shim + kopia rich_console daje #6 (CONSOLE_THEME znika) + #8 (auto-highlight) za ~15 min. Paski i struktura pozniej.

---

## ✅❌ Faza 5: Podzial Kontekstowy

### ✅ Potencjalnie DOBRE
| # | Co | Dlaczego dobre | Warunek sukcesu |
|---|----|----------------|-----------------|
| 1 | console shim w constants.py | Eliminuje ryzyko 208 importow, spelnia #5 i #6 naraz | rich_console skopiowany pierwszy |
| 2 | Kopia rich_console 1:1 (z from __future__) | Dziala od reki, przenosne | theme ma wszystkie style (zweryfikowane ✅) |
| 3 | utils/text/ dla number+chunker | Porzadek, user sam zasugerowal | zmiana 1 importu w subtitle.py |
| 4 | Osobne commity per os | Rollback, testowalnosc | dyscyplina py_compile po kazdym |
| 5 | Auto-highlight = darmowe #8 | Zero dodatkowej roboty | guard _has_rich_markup dziala (jest) |

### ❌ Potencjalnie ZLE
| # | Co | Dlaczego zle | Kiedy by zadzialalo |
|---|----|-------------|------------------------|
| 1 | Big-bang sed po 208 importach | Rozwala linie zbiorcze `from constants import a, console, b` | gdyby kazdy import byl osobny |
| 2 | Kopiowanie device.py | Ciagnie torch (ciezki) | gdyby mm_avh uzywal GPU |
| 3 | ProgressBarManager na rownoleglej ekstrakcji | 1 manager = 1 task, a tu N plikow naraz | dla sekwencyjnych operacji |
| 4 | Rewrite skopiowanych plikow na stary typing | Psuje dzialajacy kod zewnetrzny | nigdy — from __future__ zalatwia |

### ⚠️ Zalezy od kontekstu
| # | Co | Kiedy dobre | Kiedy zle |
|---|----|-------------|-----------|
| 1 | Hybryda pasow (import prywatnych kolumn) | User chce max ladne dynamiczne przejscia | Jesli kruchosc importu prywatnego przeszkadza -> fallback ostyluj Progress recznie |
| 2 | Kopiowanie logger/ w calosci | User chce "zeby byl" (#1) | Gdyby ciagnal ciezkie deps — sprawdzic __init__ |
| 3 | Delegacja do Codex | Weryfikacja koncowa, swieze oko | Zbedne przy trywialnym shim |

---

## 🏆 Faza 6: REKOMENDACJA FINALNA

### Wybrany: **K1 — chirurgiczny cherry-pick + console shim + hybryda pasow, wykonane w 4 osobnych commitach**
**Ocena koncowa:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10)

### Dlaczego ten?
Najwyzszy wynik matrycy (8.55), a co wazniejsze — **rozwiazuje najwieksze ryzyko (os D, 208 importow) trikiem shim** zamiast ryzykownego big-bang. `constants.py` re-eksportuje `console` z `rich_console` -> CONSOLE_THEME znika (#6 ✅), zero zmian w 11 plikach (#5 ✅), auto-highlight daje ladniejsze kolory za darmo (#8 ✅). Chirurgiczny cherry-pick omija torch/smieci. Osobne commity (Pomysl 7) daja rollback i testowalnosc po kazdym kroku. Wszystkie 8 zasad tablicy prawdy spelnione.

### Dlaczego NIE pozostale?
- **K3 (8.0):** prawie tak dobry, ale paski ekstrakcji mniej ladne. To wlasnie PLAN B — jesli hybryda pasow (os C) okaze sie kruchisza niz warto, schodzimy do K3. Roznica mala i odwracalna.
- **K2 (4.45):** big-bang rename zagraza #5, manager psuje render rownoleglej ekstrakcji (user juz raz dostal "martwy ekran"). Odrzucone.

### Plan B (fallback)
Jesli hybryda pasow (import prywatnych kolumn `ColoredPercentageColumn` itd.) okaze sie brzydka/krucha -> **K3**: zostaw obecny model wielu paskow ekstrakcji, ostyluj tylko `complete_style="green_bold"`/`finished_style` recznie stylami z theme. Console shim + struktura + number/chunker bez zmian. Zejscie K1->K3 dotyczy TYLKO Commitu 4.

### Kolejnosc wykonania (krytyczna)
1. Commit 1: kopia rich_console/logger/timer/safe_* (bez device/examples/tests)
2. Commit 2: utils/text/ + number/chunker + fix importu subtitle.py
3. Commit 3: console shim w constants.py (CONSOLE_THEME znika)
4. Commit 4: paski (hybryda; fallback: ostyluj Progress) + `\n` na koncu

Kazdy commit: py_compile + mypy + test importu ZANIM nastepny.
