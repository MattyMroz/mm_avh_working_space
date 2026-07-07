# zrównoleglenie pipeline — czy warto i jak

> tryb: small ideate | data: 2026-07-07
> pytanie: czy zrównoleglenie etapów (wypakowywanie MKV, przetwarzanie wyjścia)
> realnie skróci obecny czas ~5:44 przetwarzania, skoro tłumaczenie i audio są
> ograniczone limitami API?

---

## 🎯 Definicja Problemu

Pipeline `mm_avh_working_space` przetwarza wsad wideo w trybie auto. Zmierzony czas
całości: **~5 min 44 s** dla **10 plików MKV** (~0.9–1.5 GB każdy, ~13 GB łącznie).

Etapy (sekwencyjnie, każdy pętla po wielu plikach):
1. `extract_tracks_from_mkv` — mkvmerge info + mkvextract ścieżek (audio+napisy)
2. `refactor_subtitles` — ASS/SSA → SRT, split
3. `translate_subtitles` — Google/DeepL API (limit API)
4. `generate_audio_for_subtitles` — TTS ElevenBytes (85 równoległych req/plik, limit API)
5. `refactor_alt_subtitles` — SRT → ASS
6. `process_output_files` — ffmpeg x264 kodowanie MKV/MP4 (CPU-heavy)
7. `clear_temp_folders`

User chce przyspieszyć tryb auto. Ustalił: **tłumaczenie i audio zostają** (limit API =
wąskie gardło nie do obejścia). Kandydaci: **wypakowywanie MKV** i **przetwarzanie wyjścia**.

Sprzęt: **20 rdzeni CPU, dysk SSD**.

## 📐 Tablica Prawdy (Constraints)

| # | Święta Zasada (Non-Negotiable) | Źródło | Status |
|---|-------------------------------|--------|--------|
| 1 | Tłumaczenie i audio bez zmian (limit API) | user | 🔒 ABSOLUTNA |
| 2 | Równoległość dostosowana do liczby rdzeni (nie hardcode) | user | 🔒 ABSOLUTNA |
| 3 | Komentarze w kodzie po angielsku | user | 🔒 ABSOLUTNA |
| 4 | Python instructions (typing.List, guard clauses, ThreadPoolExecutor dla I/O) | repo | 🔒 ABSOLUTNA |
| 5 | Nie zepsuć istniejącego zachowania (kolejność, already_polish, error handling) | repo | 🔒 ABSOLUTNA |

---

## ⚠️ Kluczowa niewiadoma: rozkład czasu per-etap

**Timer mierzy tylko całość `main()`, nie per-etap.** Bez tego optymalizacja to częściowo
zgadywanie. Szacunek na podstawie natury etapów:

| Etap | Natura | Szacowany udział w 5:44 | Pewność |
|------|--------|------------------------|---------|
| Wypakowywanie MKV (10× ~1.3GB) | I/O + subprocess | **~30-50%** (~1.5-3 min) | średnia |
| Tłumaczenie | API (sieć) | ~15-25% | niska |
| Audio (TTS) | API (sieć, już równoległe) | ~10-20% | niska |
| Przetwarzanie wyjścia (x264) | CPU | **zależy** — czy w ogóle uruchamiane? | niska |
| Reszta (refactor, clear) | CPU lekki | <5% | wysoka |

**Wniosek wstępny:** wypakowywanie to prawdopodobnie **największy pojedynczy blok** (13 GB I/O
sekwencyjnie), więc zrównoleglenie MA sens. Ale bez pomiaru per-etap ryzykujemy optymalizację
nie tego co trzeba. → **Pomiar per-etap to zadanie #0.**

---

## 💡 Dywergencja — Pomysły

### 💡 Pomysł 1: Pomiar per-etap PRZED optymalizacją (fundament)
**Opis:** Dodać lekki timing per-etap w `main()` — log ile sekund zajął każdy krok.
**Mechanizm:** `perf_counter()` wokół każdego wywołania etapu + `console.print`.
**Mocne:** Bez danych optymalizacja to zgadywanie. To odpowiada wprost na pytanie "czy ma sens".
**Słabe:** Sam w sobie nie przyspiesza — to narzędzie diagnostyczne.
**Ryzyko:** Minimalne.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10) — warunek konieczny sensownej decyzji.
**Test tablicy prawdy:** ✅

### 💡 Pomysł 2: Wypakowywanie MKV równolegle (ThreadPoolExecutor)
**Opis:** Pętla po MKV → `ThreadPoolExecutor`, N plików naraz.
**Mechanizm:** mkvextract to subprocess I/O-bound (GIL zwalniany), wątki idealne. Limit
`min(cpu_count, len(files), CAP_IO)`. SSD → CAP_IO ~6-8 bezpieczne.
**Mocne:** Największy potencjalny zysk (13 GB I/O). SSD sprzyja. Niezależne pliki.
**Słabe:** `already_polish` (set) musi być thread-safe. Kolejność logów się miesza.
**Ryzyko:** mkvextract może konkurować o I/O — ale SSD to znosi. Przy błędzie 1 pliku nie
zabić reszty.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10)
**Test tablicy prawdy:** ✅

### 💡 Pomysł 3: Przetwarzanie wyjścia równolegle (x264)
**Opis:** `process_output_files` — kodowanie wielu plików naraz.
**Mechanizm:** ThreadPoolExecutor po plikach wyjściowych.
**Mocne:** Jest 20 rdzeni — teoretycznie miejsce na 2-3 równoległe kodowania.
**Słabe:** ⚠️ **x264 już używa wszystkich rdzeni na 1 plik.** Puszczenie N równolegle = te
same rdzenie dzielone → często **zero zysku lub wolniej** + większe zużycie RAM.
**Ryzyko:** WYSOKIE ryzyko regresji wydajności (myślisz że przyspieszasz, a spowalniasz).
**Ocena:** ⭐⭐⭐⭐☆☆☆☆☆☆ (4/10) — kontrintuicyjnie słaby kandydat mimo 20 rdzeni.
**Test tablicy prawdy:** ✅ (ale wątpliwy ROI)

### 💡 Pomysł 4: Konfigurowalny limit równoległości (skalowanie do rdzeni)
**Opis:** Helper `_parallelism(cap)` zwracający `min(cpu_count or 1, cap)`, użyty wszędzie.
**Mechanizm:** Jedna funkcja, różne CAP per etap (I/O vs CPU).
**Mocne:** Spełnia zasadę #2 (nie hardcode). Jedno miejsce prawdy.
**Słabe:** Trzeba dobrać CAP-y sensownie.
**Ocena:** ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10) — infrastruktura pod resztę.
**Test tablicy prawdy:** ✅

### 💡 Pomysł 5: Pipelining między etapami (odcinek A audio || odcinek B tłumaczenie)
**Opis:** Nakładanie etapów w czasie — gdy A skończy tłumaczenie, startuj audio A podczas
gdy B się tłumaczy.
**Mechanizm:** Kolejki/async orchestration między etapami.
**Mocne:** Teoretycznie największy zysk (etapy się nakładają).
**Słabe:** ⚠️ Ogromna złożoność. Przebudowa całego `main()`. Trudny debug. User wybrał
"równolegle w obrębie etapu", nie to.
**Ryzyko:** BARDZO WYSOKIE. Łamie zasadę #5 (duża zmiana zachowania).
**Ocena:** ⭐⭐⭐☆☆☆☆☆☆☆ (3/10) — over-engineering dla tego przypadku.
**Test tablicy prawdy:** ⚠️ ryzyko naruszenia #5

### 💡 Pomysł 6: Nic nie robić / odrzucić (baseline)
**Opis:** Zostawić sekwencyjnie.
**Mocne:** Zero ryzyka regresji.
**Słabe:** User wprost prosi o przyspieszenie; wypakowywanie realnie da się przyspieszyć.
**Ocena:** ⭐⭐⭐☆☆☆☆☆☆☆ (3/10)
**Test tablicy prawdy:** ✅ (ale nie realizuje celu)

---

## 📊 Matryca Porównawcza

| Kryterium | Waga | P1 Pomiar | P2 Wypak. | P3 Wyjście | P4 Limit | P5 Pipeline |
|-----------|------|-----------|-----------|------------|----------|-------------|
| ROI / zysk czasu | 30% | ⭐⭐⭐⭐☆☆☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ | ⭐⭐⭐☆☆☆☆☆☆☆ | ⭐⭐⭐☆☆☆☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ |
| Ryzyko (niższe=lepiej) | 30% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ | ⭐⭐⭐⭐☆☆☆☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ | ⭐⭐☆☆☆☆☆☆☆☆ |
| Wykonalność | 20% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐⭐⭐☆☆☆ | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ | ⭐⭐☆☆☆☆☆☆☆☆ |
| Wartość diagnostyczna | 20% | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ | ⭐⭐⭐☆☆☆☆☆☆☆ | ⭐⭐☆☆☆☆☆☆☆☆ | ⭐⭐⭐☆☆☆☆☆☆☆ | ⭐⭐☆☆☆☆☆☆☆☆ |
| **SUMA WAŻONA** | 100% | **8.0** | **7.0** | **4.0** | **6.5** | **4.2** |

## 🧠 Strategie Decyzyjne

**Pareto 80/20:** P1 (pomiar) + P2 (wypakowywanie) = ~20% wysiłku, prawdopodobnie ~80%
realnego zysku. P3/P5 = dużo wysiłku, wątpliwy zysk.

**Premortem — "za miesiąc to się nie udało, dlaczego?":**
- Zrównoleglono wyjście (P3), x264 walczył o rdzenie, było **wolniej** → user wściekły.
- Zrównoleglono bez pomiaru, okazało się że wypakowywanie to tylko 20% czasu, a 60% to API
  → prawie zero zysku mimo pracy.
- **Mitygacja:** NAJPIERW pomiar (P1), potem tylko to co pomiar potwierdzi.

**Red Team na P2 (wypakowywanie):** "Co złego w zrównolegleniu wypakowywania?"
- mkvextract 10× naraz może nasycić przepustowość SSD — ale to i tak szybciej niż sekwencyjnie
  na SSD. CAP ~6 to bezpieczny kompromis.
- Wniosek: P2 solidne.

---

## ✅❌ Podział Kontekstowy

### ✅ DOBRE w tym kontekście
| # | Co | Dlaczego dobre | Warunek |
|---|----|----------------|---------|
| 1 | Pomiar per-etap | Odpowiada na "czy ma sens" danymi | — |
| 2 | Równoległe wypakowywanie MKV | I/O-bound + SSD + 10 dużych plików | CAP skalowany do rdzeni |
| 3 | Helper skalujący do cpu_count | Zasada #2, brak hardcode | — |

### ❌ ZŁE w tym kontekście
| # | Co | Dlaczego złe | Kiedy by zadziałało |
|---|----|-------------|---------------------|
| 1 | Równoległe kodowanie x264 | x264 już zżera wszystkie rdzenie | gdyby kodowanie było 1-wątkowe |
| 2 | Pipelining etapów | Over-eng, duże ryzyko, user tego nie chce | gdyby etapy były długie i niezależne |

---

## 🏆 REKOMENDACJA FINALNA

### Wybór: **P1 (pomiar) → P4 (helper limitu) → P2 (wypakowywanie)** — w tej kolejności
**Ocena końcowa:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10 jako sekwencja)

### Dlaczego ten zestaw?
1. **P1 pomiar NAJPIERW** — bez danych nie wiadomo, czy 5:44 to głównie wypakowywanie czy
   API. Pomiar odpowiada wprost na pytanie usera "czy to ma sens". Tani, zero ryzyka.
2. **P4 helper** — spełnia świętą zasadę #2 (skalowanie do rdzeni), infrastruktura pod P2.
3. **P2 wypakowywanie** — najbezpieczniejszy realny zysk (I/O-bound, SSD, 13 GB). ThreadPool
   zgodny z Python instructions (§13: I/O-bound → ThreadPoolExecutor).

### Dlaczego NIE pozostałe?
- **P3 (wyjście x264):** kontrintuicyjnie słaby — równoległe kodowanie na współdzielonych
  rdzeniach zwykle NIE przyspiesza. Odrzucić chyba że pomiar pokaże, że to jest wąskie gardło
  ORAZ kodowanie jest lekkie.
- **P5 (pipelining):** over-engineering, duże ryzyko, user wybrał "w obrębie etapu".

### Plan B
Jeśli pomiar (P1) pokaże, że wypakowywanie to <15% czasu → P2 daje mały zysk, ale wciąż
warto (tani). Jeśli pomiar pokaże, że wyjście x264 dominuje ORAZ jest wielowątkowo-niedosycone
→ rozważyć P3 z limitem 2.

### Kluczowa uczciwość
Realistyczny oczekiwany zysk z P2: jeśli wypakowywanie to ~2 min z 5:44, a zrównoleglenie
6× skróci je do ~30-40 s → **oszczędność ~1.5 min (~25% całości)**. Nie rewolucja, ale
zauważalne. API (tłumaczenie+audio) pozostaje nieściśnięte — to fizyczna granica.
