# brief: zrównoleglenie pipeline

> status: UZGODNIONE — 2026-07-07
> źródło: `2026-07-07-zrownoleglenie-pipeline.md` | tryb: small

## tl;dr
Pipeline: ~5:44 dla 10 MKV (~13 GB). Tłumaczenie+audio = limit API (nie ruszać).
Realny kandydat: **wypakowywanie MKV** (I/O-bound, SSD, duże pliki). Kodowanie
wyjścia x264 to ślepy zaułek (już zżera wszystkie rdzenie → równoległe = wolniej).
**Bez pomiaru per-etap optymalizacja to zgadywanie** — dlatego pomiar idzie pierwszy.

## decyzja
Kolejność: **1) pomiar per-etap → 2) helper limitu (skalowany do cpu_count) →
3) równoległe wypakowywanie MKV (ThreadPoolExecutor, CAP ~6)**. x264 i pipelining
odrzucone (słaby ROI / duże ryzyko).

## zadania
### 🔴 krytyczne
- [ ] **Pomiar per-etap:** `perf_counter()` wokół każdego etapu w `main()` → log sekund → **rezultat:** wiadomo GDZIE idzie 5:44
- [ ] **Helper `_parallelism(cap)`:** `min(cpu_count or 1, cap)` → **rezultat:** limit skalowany do rdzeni, zero hardcode (zasada #2)

### 🟡 wysokie
- [ ] **Równoległe wypakowywanie:** ThreadPoolExecutor w `extract_tracks_from_mkv`, thread-safe `already_polish`, błąd 1 pliku nie zabija reszty → **rezultat:** wypakowywanie N× szybsze

### 🟢 normalne (warunkowe — tylko jeśli pomiar potwierdzi)
- [ ] **x264 wyjście:** TYLKO jeśli pomiar pokaże, że to wąskie gardło i kodowanie jest niedosycone → limit 2

## ryzyka
| ryzyko | trigger | akcja |
|--------|---------|-------|
| Optymalizacja nie tego etapu | pomiar pokazuje API dominuje | zaakceptować mały zysk, nie ruszać API |
| x264 wolniejszy równolegle | równoległe kodowanie | NIE zrównoleglać wyjścia domyślnie |
| SSD I/O nasycone | CAP za wysoki | CAP ~6, nie wszystkie 10 naraz |

## otwarte pytania
- ❓ Czy `process_output_files` (x264) w ogóle jest uruchamiane w typowym auto? (pomiar odpowie)
- ❓ Realny oczekiwany zysk: ~25% całości (jeśli wypakowywanie to ~2 min) — akceptowalne?
