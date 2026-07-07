# brief: migracja utils/ z mangashift + ladne paski postepu

> status: UZGODNIONE — 2026-07-08
> zrodlo: `2026-07-08-migracja-utils-i-paski-postepu.md` | tryb: big

## tl;dr
Przeniesc bogaty utils/ z MangaShift do mm_avh (rich_console, logger, timer), podmienic number_in_words/text_chunker na nowsze z gemini, wpiac ladne paski. Najwieksze ryzyko: migracja `console` (208 importow w 11 plikach). Rozwiazanie: **shim** — `constants.py` re-eksportuje `console` z `rich_console`, wiec zero zmian w 11 plikach, a CONSOLE_THEME znika. Auto-highlighting z rich_console daje ladniejsze kolory za darmo.

## decyzja
**K1: chirurgiczny cherry-pick + console shim + hybryda pasow, 4 osobne commity.** Bez torch, bez big-bang rename, kazdy commit testowalny. Plan B = K3 (prostsze paski) jesli hybryda krucha.

## zadania
### 🔴 krytyczne
- [ ] **Commit 1:** kopia `rich_console/` + `logger/` + `timer/` + `safe_fs.py` + `safe_path.py` z MangaShift (BEZ device.py/secrets/_retry/examples/tests) → **rezultat:** utils/ ma bogate pakiety, py_compile OK
- [ ] **Commit 3:** `constants.py` — usun CONSOLE_THEME + `console=Console(...)` + zakomentowany blok (110-133), dodaj `from utils.rich_console.console import console` → **rezultat:** #6 spelnione, 11 plikow dziala bez zmian, auto-highlight ON

### 🟡 wysokie
- [ ] **Commit 2:** `utils/text/__init__.py` + number_in_words+text_chunker z gemini, fix importu w `modules/subtitle.py` (`from utils.text import ...`), usun stare plaskie → **rezultat:** number/chunker w podfolderze text/
- [ ] **Commit 4:** paski ekstrakcji (start.py) + mkvtoolnix — hybryda (ostyluj Progress stylami z theme) + `\n` po ostatnim pasku → **rezultat:** ladne kolorowe paski, #7 i #8

### 🟢 normalne
- [ ] Sprawdz `__init__.py` rich_console/logger czy nie ciagnie pominietych plikow (przytnij jesli tak)
- [ ] Wizualna kontrola auto-highlight (czy nie psuje istniejacego markupu — guard _has_rich_markup jest)
- [ ] cool_animation/execution_timer ZOSTAJA plasko (YAGNI, nie ruszac)

## ryzyka
| ryzyko | trigger | akcja |
|--------|---------|-------|
| __init__ ciagnie device/torch | ImportError przy kopii | przytnij __init__, nie kopiuj device.py |
| ProgressBarManager zly na rownoleglej ekstrakcji | balagan renderu / martwy ekran | NIE manager na ekstrakcji — hybryda, fallback K3 |
| auto-highlight psuje markup | linie wygladaja inaczej | guard _has_rich_markup jest; kontrola wizualna |
| cykliczny import | ImportError constants | rich_console nie importuje constants — brak cyklu (OK) |

## otwarte pytania
- ❓ Paski: hybryda (max ladne dynamiczne przejscia, import prywatnych kolumn) czy prosty fallback (ostyluj obecny Progress recznie)? — decyzja po tescie renderu w Commit 4
- ❓ logger: kopiujemy caly folder na teraz (user: "ma po prostu byc") — potwierdzone, nie podpinamy
