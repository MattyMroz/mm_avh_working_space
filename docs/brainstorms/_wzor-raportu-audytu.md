# WZÓR RAPORTU AUDYTU — [nazwa obszaru]

> Ten plik to SZABLON. Każdy subagent wypełnia go dla swojego zestawu plików.
> Styl: skrupulatna dokumentacja projektowa — OPISZ KAŻDĄ instancję (klasa, funkcja,
> metoda, stała modułowa, dataclass). Fakty z `plik:linia`. Dla każdego elementu:
> sygnatura + opis + zależności. Plus diagnoza (co działa / dług / niespójności).
> Ton rzeczowy, zero lania wody. Polski, małe litery w nagłówkach sekcji technicznych OK.

---

## 📦 obszar: [nazwa] — pliki: [lista]

**Rola obszaru w projekcie:** [1-3 zdania: za co ten zestaw plików odpowiada w potoku
ekstrakcja→napisy→TTS→merge]

**Zależności zewnętrzne obszaru:** [biblioteki: rich, deepl, edge_tts... + wewnętrzne:
z jakich modułów mm_avh ten obszar importuje]

---

## 📄 plik: `ścieżka/do/pliku.py` (N linii)

### przeznaczenie
[2-4 zdania: co ten plik robi, kto go woła, gdzie siedzi w potoku]

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `Console` | rich.console | wypisywanie kolorowego logu |
| `MkvToolNix` | modules.mkvtoolnix | ekstrakcja ścieżek |
| ... | ... | ... |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `_PROGRESS_RE` | 42 | `re.Pattern` | regex parsujący `Postęp: 42%` z stdout mkvextract |
| ... | ... | ... | ... |

### klasy

#### `class NazwaKlasy` (linia N) — [dataclass? slots? dziedziczy po X?]
**Cel:** [za co odpowiada]
**Pola (jeśli dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `filename` | `str` | — | nazwa pliku MKV do przetworzenia |
| ... | ... | ... | ... |

**Metody:**

##### `nazwa_metody(self, arg1: Typ, arg2: Typ = default) -> Zwrot` (linia N)
- **Co robi:** [1-3 zdania konkretnie]
- **Przyjmuje:** `arg1` — [co to]; `arg2` — [co to, kiedy default]
- **Zwraca:** [co i w jakiej formie; None?]
- **Efekty uboczne:** [pisze do pliku? mutuje self.X? drukuje? odpala subprocess?]
- **Woła (call graph):** [jakie inne metody/funkcje wywołuje — self._foo(), MkvToolNix.bar()]
- **Wyjątki:** [co może rzucić / co łapie]
- **Uwagi:** [TODO, bug, magic value, workaround, martwy kod — jeśli jest]

[...powtórz dla KAŻDEJ metody...]

### funkcje modułowe (poza klasami)

##### `nazwa_funkcji(arg: Typ) -> Zwrot` (linia N)
[ten sam format co metody: co robi / przyjmuje / zwraca / efekty / woła / wyjątki / uwagi]

[...powtórz dla KAŻDEJ funkcji...]

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** [konkretnie]
- **⚠️ dług techniczny / code smells:** [duplikacja, god-function, brak typów, mieszanie
  odpowiedzialności, magic numbers, hardkody, gołe except, print zamiast log — z `plik:linia`]
- **❌ niespójności ze stylem MangaShift:** [np. brak podziału na serwis/rejestr, brak
  dataclass, płaska struktura, brak dependency injection, logika w złym miejscu — porównaj
  z docelową architekturą MangaShift]
- **🔗 sprzężenia:** [z czym ten plik jest ciasno powiązany, co by pękło przy zmianie]

[...powtórz całą sekcję "plik" dla KAŻDEGO pliku w obszarze...]

---

## 🧭 podsumowanie obszaru
- **Główne odpowiedzialności:** [co ten obszar robi jako całość]
- **Największe problemy (ranking):** [1. ... 2. ... 3. ...]
- **Kandydaci do refaktoru na styl MangaShift:** [co i dlaczego — bez pisania planu,
  tylko wskazanie]
- **Pliki/funkcje martwe lub podejrzane:** [co wygląda na nieużywane]
