# 🎯 Docelowa architektura: jedno źródło prawdy dla silników i modeli

> Fable, 2026-07-06. Stan zweryfikowany grepem na `main 4e82969c` (po FALA 8a), working tree czysty.
> Odpowiedź na pytanie Matty'ego: "czy moja wizja jest wykonalna? może niewykonalna przez mappery w pipeline?"

## ⚡ Werdykt w jednym zdaniu

**TAK, Twoja wizja jest wykonalna - i w ~70% JUŻ STOI w kodzie.** To co opisałeś
(serwis nieświadomy konkretnych silników, rejestr jako jedyna prawda, pipeline układa
całość, front decyduje) to podręcznikowy wzorzec "plugin registry + dependency inversion".
Nie wymyśliłeś czegoś naiwnego - wymyśliłeś to, co robią dojrzałe systemy. Reszta tego
dokumentu pokazuje: co już działa (dużo), co jest złamane (policzalne, naprawialne)
i dokładną drogę (5 małych fal, nie 800 plików).

---

# CZĘŚĆ 1: OBRAZ DOCELOWY (po ludzku)

## Diagram: jak silnik i model płyną przez warstwy

```text
              DWA PLIKI PRAWDY (tylko je edytujesz przy dodawaniu)
   +--------------------------------+   +--------------------------------+
   | REJESTR SILNIKÓW (per domena)  |   | KATALOG MODELI (jeden wspólny) |
   | services/<domena>/engines/     |   | models/catalog.py              |
   |   __init__.py                  |   |                                |
   | "KTO umie robić tę robotę"     |   | "JAKIE pliki wag istnieją      |
   | lista engine_id -> klasa       |   |  i do kogo pasują"             |
   +---------------+----------------+   +---------------+----------------+
                   |     wszystko niżej TYLKO CZYTA      |
                   v                                     v
   +---------------------------------------------------------------------+
   | SERWIS (fasada domeny)                                              |
   | dostaje engine_id, odpala silnik z rejestru; zero if-ów per silnik  |
   +---------------------------------+-----------------------------------+
                                     v
   +---------------------------------------------------------------------+
   | PIPELINE (kroki)                                                    |
   | układa robotę: woła serwis, a w detekcji SKLEJA wyniki wielu        |
   | silników w jedno (fuzja); listy silników importuje, nie przepisuje  |
   +---------------------------------+-----------------------------------+
                                     v
   +---------------------------------------------------------------------+
   | API                                                                 |
   | GET /engines i GET /models tylko POKAZUJĄ rejestry przez HTTP;      |
   | POST /pipeline/run przyjmuje wybór usera, złe dane = błąd 422       |
   +---------------------------------+-----------------------------------+
                                     v
   +---------------------------------------------------------------------+
   | FRONT                                                               |
   | listy do pickerów bierze z API; typy pól z codegen (generated.ts);  |
   | trzyma TYLKO swoje: ładne labelki + własne domyślne wybory          |
   +---------------------------------------------------------------------+
                                     |
                       user klika -> { engine, model_id } -> POST
```

## Warstwa po warstwie: co robi, skąd bierze prawdę, czego NIE trzyma

1. **Katalog modeli** (`models/catalog.py`): jedyna lista plików-wag; wie do jakiej klasy
   silnika pasuje każdy model. NIE trzyma: nic o krokach pipeline ani o froncie.
2. **Rejestr silników** (`services/<domena>/engines/__init__.py`): jedyna lista silników
   domeny. NIE trzyma: modeli (to katalog) ani labelek (to front).
3. **Serwis** (fasada domeny): dostaje `engine_id`, patrzy w rejestr, odpala. NIE trzyma:
   żadnej wiedzy "jeśli silnik X to zrób inaczej" - dodanie silnika NIE zmienia serwisu.
4. **Pipeline** (kroki): układa logiczną całość (np. detekcja wieloma silnikami naraz
   i sklejenie wyników). Listy silników IMPORTUJE z rejestrów. NIE trzyma: własnych,
   przepisanych ręcznie kopii tych list.
5. **API**: okno wystawowe - pokazuje rejestry (`GET /engines`, `GET /models`,
   `GET /pipeline/steps`) i waliduje to, co front przysłał. NIE trzyma: własnych list.
6. **Front**: pobiera listy z API, typy pól dostaje automatem z `bun run codegen:api`.
   Trzyma TYLKO to, co jest jego: labelki po ludzku i domyślnie zaznaczone opcje
   (bo "front decyduje" - to Twoja zasada nadrzędna, domyślny WYBÓR jest frontu).

## Kluczowa zasada: dodajesz silnik -> dotykasz ILU miejsc?

Docelowo, uczciwie policzone:

| Co dotykasz | Ile | Dlaczego to osobne miejsce |
|---|---|---|
| folder kodu silnika | 1 | to jest sam silnik, musi gdzieś żyć |
| wpis w rejestrze domeny | 1 | dwie linijki OBOK SIEBIE w jednym pliku (patrz niżej) |
| wpis w katalogu modeli | 1 per model | tylko jeśli silnik ma pliki wag do pobrania |
| plik "tłumacza wyników" | 1 | TYLKO detekcja (patrz "mappery" niżej) |
| front | 0 | typy i listy wchodzą same (codegen + API) |

Czyli: **zwykły silnik = 2 miejsca** (kod + wpis w rejestrze), silnik z modelem = 3,
silnik detekcji = 3-4. Front zero.

### Czemu nie zawsze dokładnie 1? (bez ściemy)

Bo te miejsca odpowiadają na RÓŻNE pytania. Analogia: zatrudniasz kucharza do restauracji.

- Wpis na **listę zmian** (rejestr silników): "taki człowiek u nas pracuje".
- Jego **noże do magazynu** (katalog modeli): magazyn ma własny spis, bo narzędzia
  bywają współdzielone i żyją dłużej niż jeden kucharz.
- Jeśli pisze zamówienia cyrylicą - **kartka z tłumaczeniem** dla kelnerów (mapper):
  tylko wtedy, gdy jego "język wyników" różni się od reszty.
- **Menu drukuje się samo** z listy zmian (front przez API + codegen) - nie przepisujesz go.

Zlanie tego w jedno miejsce byłoby możliwe tylko przez sklejenie magazynu z kadrami -
brzmi jak "jedno źródło", a naprawdę robi się jeden wielki plik, w którym wszystko
zależy od wszystkiego. Jedno źródło prawdy znaczy: **każde PYTANIE ma dokładnie jedno
miejsce z odpowiedzią** - nie: "wszystkie odpowiedzi w jednym pliku".

### Czemu w rejestrze to samo słowo pada dwa razy? (Literal, po ludzku)

W pliku rejestru nazwa silnika występuje 2 razy: raz w "liście na żywo" (mapie, z której
program korzysta gdy działa) i raz w "liście na papierze" (typie, który kontroler typów
i generator kontraktu dla frontu czytają BEZ uruchamiania programu - tylko dzięki temu
front dostaje podpowiadanie `"one_ocr" | "paddle_ocr"` zamiast gołego stringa).
Python nie umie zrobić jednej listy, która jest obiema naraz - to fizyka języka, nie dług.
Dlatego standard mówi: obie listy leżą **linijka pod linijką w tym samym pliku**, a dwóch
strażników (mypy + test synchronizacji) krzyczy, gdy się rozjadą. To jedna teczka
z dwiema kartkami, nie dwa źródła prawdy rozsiane po repo.

---

# CZĘŚĆ 2: DIAGNOZA STANU DZIŚ (grep-fakty)

## Tabela per domena

"Kopie listy" = miejsca, gdzie lista silników domeny jest dziś RĘCZNIE przepisana
(poza rejestrem-prawdą i poza wygenerowanym `generated.ts`, który jest legalną pochodną).

| Domena | Serwis niezależny od dodania silnika? | Rejestr-prawda | Ręczne kopie listy dziś | Front z API? |
|---|---|---|---|---|
| detection | TAK (brak fasady; buduje `runtime/factory` z katalogu) | `pipeline/detection/mappers/__init__.py:65` (10 silników) | `pipeline/detection/types.py:37` (Literal, 10 wartości przepisanych) · `services/detection/engines/__init__.py:14` (martwe lustro, konsumenci: tylko 2 pliki testów) · front `detection-engines.ts:16-89` + `:95` | **TAK** (`use-detection-engine-families.ts:13` - jedyna domena!) |
| ocr | TAK (`engines/__init__.py:42` czysty registry-lookup) | `services/ocr/engines/__init__.py:22` (2) | `services/ocr/config.py:8` (`OcrEngineName`) · `pipeline/ocr/types.py:32` (`OcrEngineId`) - DUBEL · front `types.ts:20` (`OCR_ENGINE_ID_VALUES`) | NIE |
| inpainting | TAK (`engines/__init__.py:75-81` forwarduje pola introspekcją, zero if-ów) | `services/inpainting/engines/__init__.py:23` (2) | `services/inpainting/config.py:8` (Literal; pipeline go importuje - najlepszy wzorzec, tylko zły plik) · front `types.ts:24,27` (modele + mapa model->silnik!) | NIE |
| translation | prawie (guard `if name=="llm"` w pliku rejestru `engines/__init__.py:66` - walidacja, nie dispatch) | `services/translation/engines/__init__.py:20` (3) | `pipeline/translation/types.py:28` (4 wartości: +`copy_original`, tryb kroku - celowe) · front `pipeline-translation-picker.tsx:15` | NIE |
| tts | TAK | `services/tts/engines/__init__.py:23` (4) | `pipeline/tts/types.py:27` (Literal) + `:38` (`ENGINES_WITH_MODEL_CHOICE` - zdolność silnika trzymana w pipeline!) · front `types.ts:102,105` (elevenlabs hardkod) | NIE |
| llm | NIE do końca: `services/llm/service.py:83,86` (`if provider=="gemini"/elif=="anthropic"` w validate_key) | `services/llm/engines/__init__.py:20` (6) | front `types.ts:82` (`LLM_PROVIDER_ID_VALUES`, 6 przepisanych) · `providers/types.ts:1` + `providers-card.tsx:32` (9 providerów) | NIE |
| image_processing | TAK | `services/image_processing/engines/__init__.py:21` (1) | brak kopii, ALE domena w ogóle nie wychodzi przez `GET /engines` | NIE (nie ma czego) |

## ✅ Co JUŻ działa dokładnie według Twojej wizji (to nie jest ruina)

Twoje punkty wizji, odhaczone w kodzie:

1. **"mamy listę wszystkich modeli w model registry"** - JEST: `MODEL_CATALOG`
   (27 wpisów, `models/catalog.py:1048-1411`), każdy wpis wie, którą klasę silnika odpala
   (`service_path`/`config_path`). Dodanie modelu do istniejącego silnika = 1 wpis
   w katalogu, `runtime/factory.py:62` (`_inject_model_id`) wstrzykuje `model_id` sam.
   API wystawia katalog: `GET /models` (`api/routers/models.py:94`).
2. **"serwis używa enginów, nieważne lokalny/API"** - JEST: 7/7 domen ma rejestr
   z lazy-importem po ścieżce modułu; ten sam wzorzec dla lokalnego lama i chmurowego deepl.
3. **"dodanie engina nie zmienia kodu serwisu"** - JEST w 6.5/7 domen (jedyne odstępstwo:
   `llm/service.py:83-88`, patrz niżej). Fasady nie mają if-ów per silnik - grep czysty.
4. **"pipeline układa z silników logiczną całość"** - JEST i to klasa światowa:
   fuzja cross-engine (`fusion/reconciler.py:57`), kroki jako klocki
   (`STEP_REGISTRY`, dodanie kroku = pakiet + 1 wpis), rejestr kroków wystawiony
   w API (`api/routers/pipeline.py:71`).
5. **"frontend decyduje"** - JEST (epik PR #172): typowany `PipelineConfigSnapshot`
   (`pipeline/config_schema.py:43`, `extra="forbid"`), brak wartości = 422, backend
   nie zgaduje modelu (`planning.py:92-94` rzuca błąd zamiast brać domyślny).
6. **"wszędzie jedno źródło"** - `GET /engines` (`api/routers/engines.py:32`) już
   projektuje rejestry 6 domen dla frontu; `generated.ts` ma pełne typowane uniony
   (`:2999, :3190, :3567, :5411, :5488`); import-linter pilnuje granic warstw.

Pipeline dostał w audycie 8/10, worker 9/10, editor 9/10. **Fundament stoi. To, co Cię
boli, to niedokończone OKABLOWANIE ostatniej mili - nie zła architektura.**

## ❌ Gdzie wizja złamana i JAKI mechanizm ją łamie

### 1. Typy silników rozsiane w 5 różnych wzorcach (dług "8d")

Literal (lista-na-papierze) powinien leżeć obok rejestru. Dziś: ocr ma DWA
(`config.py:8` + `pipeline/ocr/types.py:32`), inpainting w złym pliku i złą składnią
(`config.py:8`), tts i detection w pipeline zamiast przy rejestrze
(`pipeline/tts/types.py:27`, `pipeline/detection/types.py:37`), llm i image_processing
nie mają wcale. Mechanizm: każdy Literal powstawał ad-hoc przy innym zadaniu, nikt nie
ustawił jednego wzorca. **Plan naprawy JUŻ ISTNIEJE i jest grep-zweryfikowany:**
`docs/brainstorms/2026-07-06-standard-tozsamosc-silnika.md` (karta 21 plików).

### 2. Front: typy bierze z codegen, ale WARTOŚCI przepisuje ręcznie (dziura FALI 5)

Masz rację, że FALA 5 jest realnie niedokończona. Połowa backendowa (typowany snapshot,
`GET /engines`, `GET /models`, rejestr kroków w API) - zrobiona. Połowa frontowa - w ~20%:
tylko detekcja czyta `GET /engines` (`use-detection-engine-families.ts:13`). Reszta
przepisuje listy ręcznie, mimo że typ ma z codegen:

- `frontend/src/features/pipeline/types.ts:20` - `OCR_ENGINE_ID_VALUES` (lista wartości OCR),
- `types.ts:24,27` - lista modeli inpaint + mapa model->silnik (to wiedza KATALOGU
  przepisana na front, a `GET /models` istnieje),
- `types.ts:82` - `LLM_PROVIDER_ID_VALUES` (6 providerów przepisanych),
- `types.ts:33,36` - lista i kolejność kroków, choć backend wystawia rejestr kroków w API,
- `api/sse.ts:51-79` - 28 typów eventów przepisanych (runtime-lustro `EventType`),
- `detection-engines.ts:95` - statyczny default listy silników detekcji.

Mechanizm: TypeScript "gubi" typy w runtime (typ nie jest wartością), a codegen do tej
pory generował tylko typy. Stąd ręczne listy `as const satisfies` - kompilator złapie
literówkę, ale NIE złapie brakującego nowego silnika (pilnuje w jedną stronę).
Naprawa: pickery karmione z `GET /engines` / `GET /models` / `GET /pipeline/steps`
(dane w runtime), typy dalej z codegen. Ręczne listy wartości - kasacja.

### 3. Sekcje configu nazywają się inaczej niż kroki (dług "8b", siedzi w stashu)

Snapshot ma sekcje `detection`/`inpainting`/`translation` (`config_schema.py:58-65`),
a kroki nazywają się `detect`/`inpaint`/`translate` (`db/models/_enums.py:188-192`).
Parser każdej domeny czyta sekcję po "drugiej" nazwie (np.
`pipeline/inpainting/types.py:120`: `required_section(..., "inpainting")`). Działa,
ale każdy musi pamiętać dwa słowa na jedną rzecz i mina czeka na opt-in kroki.
Naprawa B1 (rename sekcji na `step.value`) JUŻ ZROBIONA przez Codexa - leży w
`stash@{0}` na branchu `refactor/fala8b-wire-kanon`. Brakuje: migracji JSON-ów w DB + regen frontu.

### 4. DB trzyma stare nazwy kolumn (dług "8c", niezrobiony)

`bubble.py:72` (`detector_model`), `text_line.py:60` (`ocr_model`),
`translation.py:64` (`model_name`) - stary kanon; powinno być `model_id`
(tak jak już jest w `detection_object.py:76`). Wymaga migracji + bump SCHEMA_VERSION.

### 5. Presety nietypowane

`api/schemas/presets.py:36,47,71` - `config_json: dict[str, Any]`, jedyny relikt
"worka bez typu" w API. Po kroku 3 (sekcje) można podpiąć `PipelineConfigSnapshot`.

### 6. Drobne wyjątki od "serwis nieświadomy silników"

- `services/llm/service.py:83-88` - `validate_key` ma `if gemini / elif anthropic`
  (różne nagłówki auth per provider). Naprawa znana: przenieść do klas silników
  (FALA 4 planu głównego już to przewiduje).
- `pipeline/tts/types.py:38` - `ENGINES_WITH_MODEL_CHOICE = {"elevenlabs"}`: zdolność
  silnika ("mam wybór modelu") zapisana w pipeline zamiast przy rejestrze silników.
- `services/detection/engines/__init__.py:14` - martwe lustro rejestru detekcji
  (zero konsumentów produkcyjnych; żyje tylko dla 2 plików testów). Do kasacji za
  Twoim podpisem (lekcja StripJoiner: kasacje publicznego API tylko z sign-off).
- `api/routers/engines.py` - nie serwuje image_processing (1/7 domen poza oknem).

## 🗺️ "Mappery w pipeline = problem?" - odpowiedź WPROST

**NIE. Mappery nie łamią Twojej wizji - one ją UMOŻLIWIAJĄ.**

Mapper (po ludzku): każdy silnik detekcji zwraca wyniki w SWOIM formacie (jeden bboxy,
drugi maski, trzeci poligony). Żeby pipeline mógł je skleić w jedno, ktoś musi
przetłumaczyć każdy format na wspólny język. Mapper = jedna funkcja-tłumacz per silnik
(`pipeline/detection/mappers/<silnik>.py`). To nie jest "druga lista silników" -
to element rejestru: w detekcji rejestr mapperów (`ENGINE_REGISTRY`,
`mappers/__init__.py:65`) JEST oficjalną tablicą prawdy tej domeny (świadomy wyjątek,
zapisany w `engine-identity-standard.md:95`), bo sklejanie wyników to logika pipeline,
nie serwisu. Dowód, że mappery się nie mnożą bez potrzeby: OCR ma JEDEN wspólny mapper
bez żadnego if-a per silnik (`pipeline/ocr/mapper.py:15`) - bo wyniki OCR są jednolite.

Jedyny realny grzech wokół mapperów: `DetectionEngineId` (lista-na-papierze) leży
w innym pliku niż rejestr (`types.py:37` zamiast obok `ENGINE_REGISTRY`) i services
trzyma martwe lustro. Oba naprawia krok K1.

---

# CZĘŚĆ 3: CZY WIZJA WYKONALNA - werdykt i ile źródeł realnie zostaje

**TAK - z jednym uczciwym zastrzeżeniem fizyki.**

Docelowo, per silnik, zostają te miejsca (i żadne więcej):

1. **Kod silnika** (folder) - nie jest "kopią listy", jest silnikiem.
2. **Jeden wpis rejestrowy** - słowo pada 2x (mapa + typ), ale linijka pod linijką
   w JEDNYM pliku, z mypy i testem jako strażnikami. To zastrzeżenie fizyki: typów
   statycznych nie da się wygenerować z działającego słownika. Nieusuwalne w Pythonie -
   ale zamknięte w jednej sekcji jednego pliku przestaje być problemem.
3. **Wpis w katalogu per model** - inna encja (plik wag), inne pytanie, własne miejsce.
4. **Mapper - tylko detekcja** - bo tylko tam formaty wyników się różnią i tylko tam
   jest fuzja. Rejestr mapperów = rejestr domeny (jedno miejsce, nie dwa).
5. **Front: zero obowiązkowych.** Opcjonalnie labelka - celowo frontowa (kanon 7 bytów:
   `label` żyje TYLKO na froncie; "PaddleOCR-VL-1.6" to decyzja UI, nie backendu).

Największe przeszkody, nazwane:

| Przeszkoda | Usuwalna? | Jak |
|---|---|---|
| typ statyczny ≠ słownik runtime (słowo 2x) | NIE (fizyka Pythona) | zamknąć w 1 pliku + strażnicy (K1) |
| front przepisuje wartości ręcznie | TAK | pickery z API, kasacja list (K4) |
| sekcje configu ≠ nazwy kroków | TAK | stash B1 + migracja JSON (K2) |
| stare kolumny DB | TAK | migracja + codegen (K3) |
| llm validate_key / TTS capability / martwe lustro | TAK | 3 małe przesunięcia (K5) |
| labelki na froncie | to NIE przeszkoda | celowa własność frontu |

---

# CZĘŚĆ 4: CO ZROBIĆ, ŻEBY TAM DOJŚĆ (plan fal)

Zasady: 1 fala = 1 branch = 1 PR = zielone CI (symulacja lokalnie przed pushem:
`ruff` + `mypy` + `lint-imports` + `pytest -m unit`). Kolejność = zależności.
Łącznie ~70-90 plików w 5-6 PR-ach. Nie 800. Każdy krok osobno bezpieczny.

## K1 - EngineId kanon (dokończenie FALI 8d) - ZACZNIJ TU

- **Co**: Literal + typowane klucze rejestru w `services/<domena>/engines/__init__.py`
  dla 7/7 domen; kasacja dubla OCR, złej składni inpainting; detection: Literal obok
  `ENGINE_REGISTRY` w mappers. Gotowy, grep-zweryfikowany plan z kartą plik:linia:
  **`docs/brainstorms/2026-07-06-standard-tozsamosc-silnika.md`** (sekcje 6-7).
- **Rozmiar**: 21 plików. Zero DB, zero zmian OpenAPI (dowód V5: diff openapi przed/po = pusty).
- **Ryzyko**: niskie/średnie (niespodzianki mypy przy typowaniu kluczy).
- **Blokuje**: K4 (czyste typy najpierw). **Wykonanie**: Opus RĘCZNIE, commit per domena
  (lekcja 8d: NIE delegować Sonnetowi zadań wymagających spójności co do słowa).
- **Decyzje usera (3, małe)**: nazwa `TranslationProviderId`; zgoda na wypisany Literal
  zamiast unii (dowód anyOf w brainstormie); ewentualny pomiar importu mapperów.
- Charakter: **MECHANICZNE z gotowym planem.**

## K2 - 8b wire: sekcje configu = nazwy kroków

- **Co**: `git stash pop stash@{0}` na branchu `refactor/fala8b-wire-kanon`
  (B1 Codexa: sekcje `detection->detect`, `inpainting->inpaint`, `translation->translate`
  + klucze engine_id; mypy przechodziło). Potem: migracja JSON-ów
  (`config_snapshot_json` w jobach + presety) + bump SCHEMA_VERSION, regen frontu
  (`bun run codegen:api`) + poprawa buildera requestu.
- **Uwaga**: plan `plan_8b.md` przepadł ze scratchpadem sesji - stash B1 to jedyny
  artefakt. Migrację trzeba rozpisać na nowo (S; wzorzec: 0034 + lekcja
  MANGASHIFT_DB_DATABASE_URL z pamięci).
- **Rozmiar**: ~15-25 plików. **Ryzyko**: średnie (migracja danych JSON - testować round-trip).
- **Blokuje**: K3 pośrednio (jedna migracja może zjeść obie? NIE - rozdzielić, patrz K3).
- Charakter: **MECHANICZNE** (B1 gotowe) + **DECYZYJNE** sign-off migracji.

## K3 - 8c: kolumny DB na kanon `model_id`

- **Co**: `bubble.detector_model` (:72), `text_line.ocr_model` (:60),
  `translation.model_name` (:64) -> `model_id`; migracja + SCHEMA_VERSION + odczyty
  w repo/usecases/schemas + regen frontu.
- **Rozmiar**: ~10-12 plików. **Ryzyko**: niskie/średnie (rename kolumn w SQLite =
  batch mode; FK-pułapki znane z 0034). **Blokuje**: nic.
- Charakter: **MECHANICZNE** + sign-off migracji.

## K4 - FALA 5 domknięcie: front przestaje przepisywać wartości

Podzielić na 4a (backend, S) i 4b (front, M):

- **4a backend**: dodać image_processing do `GET /engines` (`api/routers/engines.py`
  + schema, ~3 pliki); rozszerzyć odpowiedź engines/models tak, by front umiał
  zbudować mapę model->silnik bez ręcznej tabeli (dziś `GET /models` daje
  `engine_family`, ale nie wskazuje `engine_id` - krótki design, patrz "niepewności").
  Przenieść `ENGINES_WITH_MODEL_CHOICE` do rejestru TTS (kasacja kopii w pipeline).
- **4b front**: pickery OCR/inpaint/translation/TTS/LLM karmione z `GET /engines` +
  `GET /models` (wzorzec już istnieje: `use-detection-engine-families.ts`); kroki
  i kolejność z `GET /pipeline/steps` (już wystawione, `api/routers/pipeline.py:71`);
  kasacja: `OCR_ENGINE_ID_VALUES`, `INPAINTING_MODEL_ID_VALUES`,
  `INPAINTING_ENGINE_BY_MODEL`, `LLM_PROVIDER_ID_VALUES`, `PIPELINE_STEP_ORDER/LABELS`
  (ręczne), `DEFAULT_DETECTION_ENGINE_IDS`; `BACKEND_EVENT_TYPES` - wygenerować
  wartości z codegen (openapi-typescript ma tryb emisji enumów - do potwierdzenia,
  patrz "niepewności") albo zostawić z testem dwustronnym.
  Labelki i domyślne wybory ZOSTAJĄ na froncie (celowe).
- **Rozmiar**: ~4 + ~12-15 plików. **Ryzyko**: średnie (UI regresje - przejść pickery
  ręcznie w `bun tauri dev` + vitest). **Blokuje**: nic dalej.
- Charakter: 4a **DECYZYJNE-lite** (mały design odpowiedzi API), 4b **MECHANICZNE**.

## K5 - wyjątki i resztki (sweep, małe PR-y)

- `validate_key` z `llm/service.py:83-88` do klas silników (zbiega się z FALĄ 4 planu
  głównego - scaleniem szablonu LLM; można zrobić razem).
- Kasacja martwego lustra `services/detection/engines/_REGISTRY` + przepięcie
  2 testów-inwariantów na `_portable.ENGINE_DEPS` - **wymaga Twojego sign-off**
  (dotyka publicznego API serwisu; szczegóły w brainstormie sekcja 5b).
- Presety: `config_json: dict[str, Any]` -> `PipelineConfigSnapshot`
  (`api/schemas/presets.py:36,47,71`) - po K2, bo klucze sekcji.
- **Rozmiar**: ~10-12 plików w 2-3 małych PR-ach. **Ryzyko**: niskie.
- Charakter: **MECHANICZNE** poza jednym sign-off.

## K6 - (ficzer, osobny backlog) UPSCALE jako krok pipeline

Domena image_processing dostaje krok wg pipeline-step-standard - wtedy jej Literal
i sekcja snapshotu wchodzą tym samym wzorcem co reszta. To ficzer, nie refaktor -
nie blokuje niczego wyżej i nic go nie blokuje poza K1 (typy).

## Po K1-K5 świat wygląda tak

Dodajesz silnik OCR: piszesz folder `engines/nowy/`, dopisujesz 2 sąsiednie linijki
w `services/ocr/engines/__init__.py`, (ew. wpis modelu w katalogu), odpalasz
`bun run codegen:api`. Serwis - nietknięty. Pipeline - nietknięty. API - nietknięte.
Front - picker sam pokaże nową opcję. Dokładnie Twoja wizja.

---

# 🤔 Czego nie jestem pewny (skill end)

1. **Mapa model->silnik dla frontu (K4a)**: katalog wiąże model z klasą silnika przez
   `service_path`, nie przez `engine_id`. Zaproponowałem rozszerzenie odpowiedzi API,
   ale kształt (pole `engine_id` w `GET /models` vs lista modeli per silnik w
   `GET /engines`) wymaga 30-minutowego designu - nie przesądzam go tutaj.
2. **Emisja wartości enumów przez openapi-typescript** (K4b, `BACKEND_EVENT_TYPES`):
   wiem, że narzędzie ma tryb generowania enumów runtime, nie zweryfikowałem go
   w wersji z tego repo. Fallback jest bezpieczny: zostaje ręczna lista + test
   dwustronny (to 1 plik, nie architektura).
3. **Rozmiar migracji K2**: nie widziałem zawartości stasha B1 (nie ruszałem go, żeby
   nie mieszać w working tree) - liczba plików ~15-25 to szacunek z opisu w
   `temp/STAN-FALA8-KANON.md`, nie z diffa.
4. **Presety w DB**: nie sprawdzałem, ile istniejących wierszy presetów ma stare klucze
   sekcji - migracja K2 musi je objąć albo jawnie odciąć (decyzja przy K2).
5. **Kolejność K2 vs K3**: dałem sekcje przed kolumnami (stash gotowy = tańszy start),
   ale odwrotna kolejność też działa - jeśli wolisz zacząć od mniejszej migracji,
   zamień je miejscami bez szkody.
