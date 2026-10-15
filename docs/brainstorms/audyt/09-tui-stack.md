# 09 — Audyt stacku TUI dla mm_avh

> Badanie do decyzji architektonicznej: jaki stack terminalowego UI w Pythonie
> najlepiej pasuje do wizji "coś pomiędzy Claude Code, terminalem a apką webową
> — ale w terminalu". Stan wiedzy: lipiec 2026.

## TL;DR

- **Claude Code i Gemini CLI są napisane w JavaScript/TypeScript, nie w Pythonie.**
  Renderują UI przez **Ink** (React dla terminala, na Node/Bun). Tego stacku
  **nie da się przenieść 1:1 do Pythona** — to nie jest kwestia biblioteki, tylko
  całego ekosystemu (React + reconciler + Node).
- Dla wizji mm_avh (banner + Enter-auto + `/settings` + `/help` + autocomplete
  `/komend` + rich text) **najbliżej Claude Code przy zachowaniu PROSTOTY daje
  `prompt_toolkit` (input + inline autocomplete `/komend` + historia) + `rich`
  (rendering bannera, paneli, tabel).**
- **Textual** to najpotężniejsza opcja (pełny framework okienkowy), ale to inny
  model niż Claude Code (pełnoekranowa apka zdarzeniowa, nie płynący REPL) i jego
  wbudowany command palette to **modal na Ctrl+P z fuzzy search — nie inline
  autocomplete po wpisaniu `/`**. Więcej mocy, ale dalej od wizji i mniej "proste".
- **Sam `rich`** nie wystarczy do interaktywnego `/slash` z podpowiadaniem — to
  biblioteka renderująca, nie silnik inputu. Świetnie się jednak dokłada do każdej
  z powyższych opcji.

---

## 1. W czym jest Claude Code i Gemini CLI (fakty)

### Stack: Ink = React w terminalu (JS/Node)

Oba narzędzia renderują interfejs przez **Ink** — bibliotekę, która renderuje
komponenty React do terminala (zamiast do DOM commituje do "terminal-native host
nodes" przez `react-reconciler`). To ten sam model mentalny co apka webowa:
komponenty, `useState`, hooki, deklaratywny render — tyle że wyjściem jest tekst
w konsoli.

- **Claude Code**: wystartował na Ink, po czym forknął go i mocno zoptymalizował
  (packed typed arrays zamiast obiektu-na-komórkę, double-buffering, string
  interning) — cel: 60 fps przy streamowaniu tokenów na szerokim terminalu.
  Kod podzielony na `src/ink/` (silnik renderowania/layout) i `src/components/`
  (komponenty + design system). Startup przyspieszony przez przejście na **Bun**.
- **Gemini CLI**: również **Ink/React**. Autocomplete `/slash` i ścieżek `@plik`
  robi hook `useCommandCompletion`; input odseparowany od surowych escape-sekwencji
  przez `KeypressContext`. Dodano flagę `autoExecute` — proste komendy `/` (bez
  argumentów) odpalają się od razu po Enter, gdy wybrane z podpowiedzi.

### Co konkretnie renderuje palette `/slash` z autocomplete

To nie jest osobna biblioteka "palette" — to **własny komponent React** (input +
lista podpowiedzi + obsługa klawiszy strzałek/Enter/Tab), rysowany przez Ink w
locie pod polem wpisywania. Podpowiedzi filtrowane są na bieżąco (prefix `/`),
a wybór wstawia komendę do inputu albo ją odpala. Czyli: **inline dropdown
zintegrowany z polem tekstowym**, nie modal na skrót.

### Dlaczego to JS, a nie Python — i co to znaczy dla Ciebie

Wybór Node/TS to **path dependency i dopasowanie ekosystemu**, nie wyższość języka:

- Gdy ruszyła fala agentów LLM, Node miał już gotowy komplet dojrzałych bibliotek
  CLI (Ink, Commander.js, Chalk, Inquirer) idealnie pod ten use-case
  (terminal + streaming + integracja z IDE).
- Modele bywają lepsze w TypeScript (więcej przykładów w danych treningowych) —
  argument podawany wprost przy Gemini CLI.
- Bun rozwiązał historyczny problem wolnego startu Node.

**Konsekwencja dla mm_avh:** nie da się dostać dokładnie tego samego renderera co
Claude Code w Pythonie. Ale **efekt wizualny i UX (banner, `/komendy` z inline
autocomplete, panele, kolory, historia) da się w Pythonie odtworzyć bardzo blisko**
— innym silnikiem (`prompt_toolkit` + `rich`), nie przez React. To ważna korekta
oczekiwań: kopiujemy *doświadczenie*, nie *implementację*.

---

## 2. Kandydaci — analiza

### Textual (Textualize)

- **Wersja/utrzymanie (2026):** v8.2.8 (30.06.2026), ~36.6k gwiazdek, aktywnie
  utrzymywany. **Uwaga o kontekście:** firma Textualize (komercyjna) **zakończyła
  działalność w 2025** — Will McGugan jest na sabbatical, ale **deklaruje dalsze
  utrzymywanie Rich i Textual jako open source**. Projekt żyje, ale bez etatowego
  zespołu za nim. Warto mieć to z tyłu głowy przy długoterminowej zależności.
- **Co to jest:** pełny framework aplikacji TUI (jak "React/CSS dla terminala,
  ale w Pythonie") — event loop async, widżety, layout, TCSS (CSS dla terminala),
  reaktywne atrybuty. Zbudowany na `rich` (każdy renderable z rich działa w środku).
- **`/slash` autocomplete:** wbudowany **command palette to modal odpalany
  Ctrl+P** z fuzzy search po zarejestrowanych komendach (`SystemCommand` /
  `Provider`). **To NIE jest inline autocomplete po wpisaniu `/` jak w Claude Code.**
  Żeby uzyskać dropdown-pod-inputem, potrzebna dodatkowa biblioteka
  **`textual-autocomplete`** (darrenburns, v4.0.6 z 09.2025, ~288 gwiazdek, wymaga
  Textual ≥2.0) — działa, ale to kolejna zależność i własna robota, żeby spiąć ją
  z logiką `/komend`.
- **Reaktywne panele:** tak, to jego mocna strona — `/settings` jako panel z
  auto-zapisem i live update to naturalny use-case (reaktywne atrybuty + widżety
  Input/Switch/Select).
- **Ciężkość:** najcięższy z całej trójki — async framework, TCSS, własny system
  layoutu. To pełna apka, nie skrypt.
- **Windows:** oficjalnie wspierany (macOS/Linux/Windows), działa dobrze na
  Windows Terminal.
- **Krzywa uczenia:** najstromsza — trzeba ogarnąć model zdarzeniowy, TCSS,
  cykl życia widżetów. To realna nauka frameworka.
- **Pasuje do wizji?** Częściowo. Da radę zrobić "banner + Enter przetwarza +
  `/settings` panel" — ale **model jest inny niż Claude Code**: Claude Code to
  płynący w dół strumień (REPL-like), a Textual naturalnie ciągnie w stronę
  pełnoekranowej apki z okienkami. Dostajesz więcej mocy kosztem prostoty i
  kosztem oddalenia się od "terminala, który płynie".

### rich (sam, bez Textual)

- **Wersja/utrzymanie:** >40k gwiazdek, dojrzały, ten sam autor/status utrzymania
  co Textual. De facto standard renderowania w terminalu Pythona. **User już go zna.**
- **Co realnie umie interaktywnie:** `rich.prompt` (proste pytania z walidacją),
  `Live` (odświeżany region — progress bary, live tabele/panele — już tego używasz
  w ekstrakcji), `Console`, `Panel`, `Table`, `Syntax`, kolory, markup.
- **Granica:** **rich to renderer, nie silnik inputu.** Nie ma pola tekstowego z
  obsługą kursora, historii ani dropdownu autocomplete. `/slash` z podpowiadaniem
  i "live menu" pod inputem **nie zrobisz samym rich** — musiałbyś ręcznie czytać
  klawisze i przerysowywać, co szybko staje się reimplementacją `prompt_toolkit`.
  Oficjalna rekomendacja twórców: gdy potrzebujesz pełnej interaktywności — idź do
  Textual (albo, dla REPL-a, do prompt_toolkit).
- **Rola w mm_avh:** **zostaje** — jako warstwa renderująca banner, panele, tabele,
  progress. Nie jako silnik komend.

### prompt_toolkit

- **Wersja/utrzymanie (2026):** v3.0.52 (27.08.2025), status "Production/Stable",
  Python ≥3.8, aktywnie utrzymywany. **Lekki: jedyne zależności to Pygments i
  wcwidth.** Silnik pod IPython, ptpython, pgcli, wieloma CLI — czyli sprawdzony
  właśnie w REPL-ach z `/komendami`, autocomplete i historią.
- **`/slash` autocomplete:** to jego rdzeń. `complete_while_typing=True` daje
  **inline dropdown podczas pisania** (dokładnie ten efekt co w Claude Code).
  `NestedCompleter` daje hierarchiczne komendy (`/settings voice`, `/settings lang`),
  a własny `Completer` pozwala wykryć prefix `/` i podpowiadać tylko komendy.
  To najbliżej "podpowiadania składni jak w Claude Code" w całym Pythonie.
- **Historia / edycja:** wbudowana historia (strzałki, reverse-search), pełna
  edycja linii, keybindingi, `bottom_toolbar` (pasek statusu na dole).
- **Panele/tabele:** **nie jest od tego** — ma własne prymitywy, ale do ładnych
  paneli/tabel lepiej użyć `rich` obok. **prompt_toolkit + rich składają się
  naturalnie**: PT bierze input+autocomplete, rich renderuje resztę wyjścia.
  (Drobny cień: PT rysuje własny ekran; przy jednoczesnym `bottom_toolbar` i menu
  completions bywają ograniczenia layoutu — ale dla wizji mm_avh to nieblokujące.)
- **Windows:** działa (PT explicite wspiera Windows; IPython/pgcli na Windows na
  nim stoją).
- **Krzywa uczenia:** średnia — API completerów i keybindingów trzeba poznać, ale
  to wciąż "biblioteka do pętli inputu", nie cały framework okienkowy.
- **Pasuje do wizji?** **Najlepiej z całej trójki** pod kątem "REPL jak Claude Code
  z inline `/autocomplete`", przy zachowaniu prostoty (skrypt, nie apka okienkowa).

### Kombinacje

- **prompt_toolkit (input + `/autocomplete` + historia) + rich (banner, panele,
  tabele, progress) — REKOMENDOWANE.** Każda robi to, w czym jest najlepsza,
  obie lekkie, obie sprawdzone, obie już częściowo w Twoim świecie (rich znasz).
- **Textual robi oba naraz** (input i rendering w jednym frameworku) — ale kosztem
  ciężkości, innego modelu (okienka zamiast płynącego REPL-a) i dodatku
  `textual-autocomplete` do inline dropdownu. Więcej mocy, mniej prostoty.
- **Sam rich** — niewystarczający do interaktywnego `/slash`.

---

## 3. Tabela porównawcza

| Biblioteka | `/slash` inline autocomplete | Live panele / reaktywność | Ciężkość (zależności) | Windows | Krzywa uczenia | Pasuje do wizji mm_avh? |
|---|---|---|---|---|---|---|
| **prompt_toolkit** | ✅ Natywnie (`complete_while_typing`, `NestedCompleter`, custom `/` completer) — rdzeń biblioteki | ⚠️ Słabo (renderer nie od tego) — dokładasz `rich` | 🟢 Lekki (Pygments + wcwidth) | ✅ | 🟡 Średnia | ✅✅ **Najbliżej Claude Code przy prostocie** |
| **rich (sam)** | ❌ Nie (renderer, nie input) | ⚠️ `Live` = odświeżany region; brak reaktywnych widżetów | 🟢 Lekki | ✅ | 🟢 Niska (już znasz) | ⚠️ Tylko jako warstwa renderująca, nie silnik komend |
| **Textual** | ⚠️ Wbudowany palette = modal na Ctrl+P (fuzzy), nie inline `/`; inline wymaga `textual-autocomplete` | ✅✅ Mocna strona (reaktywne widżety, TCSS) | 🔴 Ciężki (async framework, TCSS, layout) | ✅ | 🔴 Stroma | ⚠️ Da radę, ale inny model (okienka) niż płynący REPL Claude Code |
| **prompt_toolkit + rich** | ✅ (z PT) | ✅ (z rich: panele/tabele/progress) | 🟢 Lekki (suma dwóch lekkich) | ✅ | 🟡 Średnia | ✅✅✅ **Rekomendacja** |

Referencyjnie: **Claude Code / Gemini CLI = Ink (React, JS/Node)** — inline
`/autocomplete` przez własny komponent React; **nie do odtworzenia 1:1 w Pythonie**,
ale UX najbliżej replikuje `prompt_toolkit` + `rich`.

---

## 4. Rekomendacja pod konkretną wizję

**`prompt_toolkit` (input + `/autocomplete` + historia) + `rich` (banner, panele,
tabele, progress).**

Dlaczego to, a nie pozostałe:

1. **Najbliżej Claude Code w tym, co widać.** Płynący REPL z bannerem na górze,
   Enter uruchamia akcję, wpisanie `/` pokazuje **inline dropdown komend** —
   to dokładnie model Claude Code, a `prompt_toolkit` daje go natywnie
   (`complete_while_typing`). Textual tego z pudełka nie ma (jego palette to modal
   na Ctrl+P), a sam rich nie ma inputu.
2. **Prostota (Twój priorytet).** To wciąż "pętla: wczytaj komendę → wyrenderuj
   wynik", a nie pełny framework okienkowy z event loopem, TCSS i cyklem życia
   widżetów. Mniej do nauczenia, mniej do utrzymania, łatwiej debugować.
3. **Lekkość.** PT = Pygments + wcwidth; rich = jedna dojrzała zależność.
   Zero ciężkiego async-frameworka.
4. **rich już znasz i używasz** (progress ekstrakcji). Dokładasz tylko PT jako
   warstwę inputu — nie przepisujesz renderowania.
5. **Bezpieczeństwo utrzymania.** Oba dojrzałe i aktywne w 2026. (Textual też żyje,
   ale za nim nie stoi już firma — dla długoterminowej zależności lekki niuans.)

**Kiedy rozważyć Textual zamiast tego:** jeśli w przyszłości `/settings` urośnie
do rozbudowanego, pełnoekranowego panelu z wieloma zakładkami, formularzami i
live-podglądem (bardziej "apka" niż "REPL"). Wtedy reaktywne widżety i TCSS
Textuala zaczynają się opłacać mimo stromszej krzywej. Na start i pod obecną wizję
— to nadmiar (over-engineering).

**Sam rich** odpada jako całość rozwiązania (brak inputu/autocomplete), ale
**zostaje jako warstwa renderująca** wewnątrz rekomendowanego stacku.

---

## 5. Szkic — jak wyglądałby taki panel (prompt_toolkit + rich)

Minimalny szkielet: banner, pętla komend, inline autocomplete `/komend`,
`/settings`, `/help`, Enter-auto. **Kod poglądowy** (nie produkcyjny).

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

COMMANDS = {
    "/auto":     "Automatyczne przetworzenie folderu",
    "/manual":   "Tryb ręczny — wybór kroków",
    "/settings": "Panel ustawień (auto-zapis)",
    "/help":     "Lista komend",
    "/exit":     "Wyjście",
}


class SlashCompleter(Completer):
    """Podpowiada /komendy dopiero po wpisaniu '/', jak w Claude Code."""
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        if not text.startswith("/"):
            return
        for cmd, desc in COMMANDS.items():
            if cmd.startswith(text):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display_meta=desc,  # opis obok podpowiedzi
                )


def banner() -> None:
    console.print(Panel.fit(
        "[bold cyan]mm_avh[/]  ·  terminalowy CLI do anime",
        border_style="cyan",
    ))


def show_help() -> None:
    table = Table(title="Komendy", show_header=True, header_style="bold")
    table.add_column("Komenda", style="cyan")
    table.add_column("Opis")
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(table)


def open_settings() -> None:
    # /settings: tu panel z auto-zapisem (rich renderuje, PT wczytuje wartości)
    console.print(Panel("[bold]Ustawienia[/] — auto-zapis włączony", border_style="green"))
    # ... pola: session.prompt("Głos TTS: ", default=...) + zapis do configu


def main() -> None:
    banner()
    session = PromptSession(
        history=InMemoryHistory(),
        completer=SlashCompleter(),
        complete_while_typing=True,       # inline dropdown w trakcie pisania
        bottom_toolbar="Enter = auto · /help = komendy · Ctrl+C = wyjście",
    )
    while True:
        try:
            line = session.prompt("mm_avh ▸ ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if line == "":              # Enter bez tekstu → auto (wizja: Enter przetwarza)
            console.print("[green]▶ Przetwarzam folder...[/]")
            # process_folder()
        elif line == "/help":
            show_help()
        elif line == "/settings":
            open_settings()
        elif line in ("/exit", "/auto", "/manual"):
            if line == "/exit":
                break
            console.print(f"[cyan]{line}[/] — TODO")
        elif line.startswith("/"):
            console.print(f"[red]Nieznana komenda:[/] {line}  (/help)")
        else:
            console.print(f"[dim]{line}[/]")


if __name__ == "__main__":
    main()
```

Kluczowe punkty szkicu:
- **Inline autocomplete `/komend`** = `SlashCompleter` + `complete_while_typing=True`.
  Wpisanie `/se` pokazuje dropdown z `/settings` i opisem — jak w Claude Code.
- **Enter-auto** = pusta linia uruchamia przetwarzanie folderu.
- **rich** rysuje banner, tabelę `/help`, panel `/settings`, statusy — kolory i
  ramki "za darmo".
- **Historia** (strzałka w górę) i **`bottom_toolbar`** (pasek podpowiedzi na dole)
  z PT gratis.
- Hierarchię (`/settings voice`) można później podnieść na `NestedCompleter`.

---

## 6. Ryzyka i pułapki

- **Oczekiwanie "1:1 jak Claude Code" jest niespełnialne.** To Ink/React na Node;
  w Pythonie odtwarzamy UX, nie renderer. Jasno to zakomunikować, żeby nie gonić
  za 60-fps streamowaniem i pixel-perfect zachowaniem — to nie jest cel mm_avh.
- **prompt_toolkit + rich: dwa światy renderowania.** PT zarządza polem inputu i
  swoim ekranem, rich renderuje wyjście między promptami. To działa (tak robi wiele
  CLI), ale nie mieszaj ich w tym samym momencie rysowania. Przy jednoczesnym
  `Live` z rich i aktywnym promptcie PT trzeba uważać — najprościej: **rich
  renderuje, gdy PT nie trzyma prompta** (sekwencyjnie, nie na tej samej klatce).
- **Textual = over-engineering pod obecną wizję.** Async event loop, TCSS, cykl
  życia widżetów i dodatek `textual-autocomplete` to dużo maszynerii, żeby dostać
  to, co PT+rich daje prościej. Sięgaj po Textual dopiero, gdy `/settings` realnie
  urośnie do wieloekranowej apki — inaczej zabijasz priorytet "PROSTOTA".
- **Sam rich kusi, ale jest ślepą uliczką dla `/slash`.** Ręczne czytanie klawiszy
  i przerysowywanie menu to reimplementacja prompt_toolkit — nie idź tą drogą.
- **Utrzymanie Textualize bez firmy.** Rich i Textual żyją i są utrzymywane przez
  autora, ale komercyjny podmiot za nimi zniknął (2025). Dla PT ryzyko mniejsze
  (inny, stabilny maintainer, fundament IPython/pgcli). Niski, ale realny czynnik
  przy wyborze długoterminowej zależności.
- **Autocomplete tylko dla `/` — pilnuj UX.** Completer ma podpowiadać komendy
  wyłącznie po `/` (jak w szkicu), żeby nie zaśmiecać zwykłego wpisywania ścieżek
  czy tekstu. Prosty warunek `startswith("/")` załatwia sprawę.

---

## Źródła

- [Claude Code Internals, Part 11: Terminal UI (Medium)](https://kotrotsos.medium.com/claude-code-internals-part-11-terminal-ui-542fe17db016)
- [UI Layer (Ink/React Terminal) — DeepWiki](https://deepwiki.com/farion1231/claude-code/10-ui-layer-(inkreact-terminal))
- [How Claude Code Uses React in the Terminal (DEV)](https://dev.to/vilvaathibanpb/how-claude-code-uses-react-in-the-terminal-2f3b)
- [I studied Claude Code's leaked source and built a terminal UI toolkit (DEV)](https://dev.to/minnzen/i-studied-claude-codes-leaked-source-and-built-a-terminal-ui-toolkit-from-it-4poh)
- [Gemini CLI Project Architecture Analysis](https://gemini-cli.xyz/docs/en/architecture-analysis)
- [Gemini CLI — Interactive Mode and Basic Usage (DeepWiki)](https://deepwiki.com/google-gemini/gemini-cli/3.1-interactive-mode-and-basic-usage)
- [PR #13985 — auto-execute simple slash commands on Enter (gemini-cli)](https://github.com/google-gemini/gemini-cli/pull/13985)
- [Why Most Coding Agents Are Built with Node.js (BSWEN)](https://docs.bswen.com/blog/2026-06-27-why-most-coding-agents-are-built-with-nodejs/)
- [Textual — GitHub](https://github.com/Textualize/textual)
- [Textual — Command Palette (docs)](https://textual.textualize.io/guide/command_palette/)
- [The future of Textualize (blog)](https://textual.textualize.io/blog/2025/05/07/the-future-of-textualize/)
- [textual-autocomplete — GitHub](https://github.com/darrenburns/textual-autocomplete)
- [prompt-toolkit — PyPI](https://pypi.org/project/prompt-toolkit/)
- [Python Prompt Toolkit 3.0 — docs](https://python-prompt-toolkit.readthedocs.io/)
- [prompt_toolkit — Asking for input (completion) docs](https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html)
- [ptpython — GitHub](https://github.com/prompt-toolkit/ptpython)
- [Rich — GitHub](https://github.com/textualize/rich)
- [The Python Rich Package (Real Python)](https://realpython.com/python-rich-package/)
- [10 Best Python TUI Libraries for 2025 (Medium)](https://medium.com/towards-data-engineering/10-best-python-text-user-interface-tui-libraries-for-2025-79f83b6ea16e)
