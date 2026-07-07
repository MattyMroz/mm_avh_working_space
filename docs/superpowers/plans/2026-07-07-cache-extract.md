# Cache ekstrakcji MKV (B1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Pominąć ponowną ekstrakcję ścieżki z MKV, jeśli plik wynikowy już istnieje
i jest kompletny — przy powtórnych biegach oszczędza cały etap ekstrakcji tego pliku.

**Architecture:** Guard przed `mkvextract`: jeśli docelowy plik istnieje i ma rozmiar
powyżej progu, log "pomijam" i przejdź do następnej ścieżki. Zmiana punktowa w
`mkv_extract_track`, zero zmian architektury.

**Tech Stack:** Python 3.10+, subprocess (mkvextract), os.path/os.stat.

## Global Constraints

- Python ≥3.10; komentarze w kodzie po angielsku
- Nie zmieniać zachowania trybu manualnego ani auto poza pominięciem istniejących plików
- Guard oparty na rozmiarze (kompletność) — niekompletny/pusty plik NIE może być uznany za cache
- Zgodność z Python instructions: guard clause, typing

---

### Task 1: Guard cache w mkv_extract_track

**Files:**
- Modify: `modules/mkvtoolnix.py` — pętla ekstrakcji w `mkv_extract_track` (obecnie linie ~229-241)

**Interfaces:**
- Consumes: `self.working_space_temp`, `self.filename`, `self._get_format_extension`,
  `self._get_extract_command` (istniejące).
- Produces: brak nowego publicznego API — tylko wewnętrzna zmiana zachowania pętli.

- [ ] **Step 1: Dodaj stałą progu rozmiaru**

W sekcji stałych modułu (góra `mkvtoolnix.py`, po importach) dodaj:

```python
# Below this size an extracted track is treated as incomplete/garbage, so the
# cache guard re-extracts it instead of trusting a truncated leftover file.
MIN_EXTRACTED_BYTES: int = 1024
```

- [ ] **Step 2: Wstaw guard w pętli ekstrakcji**

W `mkv_extract_track`, w pętli `for track_id in tracks_to_extract:`, PO wyliczeniu
`out_file`, a PRZED budową `command`, wstaw guard:

```python
                filename: str = f'{self.filename[:-4]}.{format_extension}'
                out_file: str = path.join(self.working_space_temp, filename)

                # Skip re-extraction when a complete file is already there — this
                # makes repeated runs skip the whole extraction of that track.
                if path.isfile(out_file) and stat(out_file).st_size >= MIN_EXTRACTED_BYTES:
                    console.print(
                        f'Pomijam ekstrakcję (plik już istnieje): {filename}',
                        style='green_bold')
                    continue

                command: List[str] = self._get_extract_command(
                    track_id, out_file)
```

- [ ] **Step 3: Dodaj import stat (jeśli brak)**

Sprawdź górę pliku. Jeśli jest `from os import path`, zmień na:

```python
from os import path, stat
```

- [ ] **Step 4: Weryfikacja — kompilacja + test guardu**

Run:
```bash
cd "c:/Users/MattyMroz/Desktop/PROJECTS/mm_avh_working_space" && python -m py_compile modules/mkvtoolnix.py && echo OK
```
Expected: `OK`

Test logiki guardu (bez realnego MKV — sprawdzamy warunek):
```bash
uv run python -c "
import os, tempfile
from os import path, stat
from modules.mkvtoolnix import MIN_EXTRACTED_BYTES
scratch = tempfile.mkdtemp()
# plik kompletny (>= prog) -> guard pomija
big = os.path.join(scratch, 'a.aac'); open(big,'wb').write(b'x'*2048)
assert path.isfile(big) and stat(big).st_size >= MIN_EXTRACTED_BYTES
# plik pusty/za maly -> guard NIE pomija (re-ekstrakcja)
small = os.path.join(scratch, 'b.aac'); open(small,'wb').write(b'x'*10)
assert not (path.isfile(small) and stat(small).st_size >= MIN_EXTRACTED_BYTES)
print('guard OK: kompletny pomijany, niekompletny re-ekstrahowany')
"
```
Expected: `guard OK: ...`

- [ ] **Step 5: Commit**

```bash
git add modules/mkvtoolnix.py
git commit -m "perf: cache ekstrakcji MKV — pomiń gdy plik już istnieje (B1)"
```

---

## Self-Review

- **Spec coverage:** B1 z briefu (cache extract, guard path.exists+rozmiar) → Task 1. ✅
- **Placeholder scan:** brak TBD/TODO; cały kod podany. ✅
- **Type consistency:** `MIN_EXTRACTED_BYTES: int`, `stat().st_size` int — spójne. ✅
- **Ryzyko:** guard oparty na rozmiarze — niekompletny plik (<1024 B) jest re-ekstrahowany,
  więc nie zostawiamy śmiecia. Zgodne z constraint.
