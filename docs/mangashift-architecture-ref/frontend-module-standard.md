# Frontend Module Standard

Standard obowiazuje KAZDY modul frontu: `frontend/src/features/<domena>/` i
`frontend/src/features/editor/modules/<domena>/`. Editor to nie wyjatek, tylko grupa modulow tego
samego ksztaltu + trzy warstwy wlasne (`core/`, `shell/`, `canvas/`) opisane w tym dokumencie.
To frontowy odpowiednik [service-standard.md](service-standard.md) - ta sama filozofia:
**modul = niezalezny klocek z czystym, minimalnym, jawnym API**.

> Zrodlo decyzji: `docs/archive/2026-06/2026-06-29-refaktor-struktury-edytora-frontend.md` (ideacja big).
> Tablica prawdy: prostota, anti-szkielet, klocki jak backend services, jeden edytor 2 tryby.

## Cel

- Modul frontu ma byc samodzielnym klockiem domenowym (np. `projects`, `pipeline`, `detection`).
- Modul ma JEDNO jawne publiczne API w `index.ts` (barrel selektywny) - jak `__init__.py` serwisu backendu.
- Wnetrze modulu (components/, api/, store/, model/) jest niewidoczne dla innych - tylko przez barrel.
- Dodanie pokrewnego ficzera = zmiana w TYM module, nie rozlewanie sie na inne.
- Modul nie zna HTTP detali poza swoim `api/` (warstwa danych); UI nie zna fetchowania bezposrednio.
- ZERO pustych folderow - szablon jest ELASTYCZNY, modul ma tylko to co realnie robi (anti-szkielet).

## Filozofia: jeden edytor, dwa tryby

Edytor to JEDEN byt o dwoch trybach (`image` | `video`), nie dwa edytory. Moduly sa WSPOLDZIELONE miedzy
trybami. Regula: warstwy/klocki sie PRZENOSI miedzy trybami, nie DUPLIKUJE. Tryb decyduje tylko CO
montuje `shell/` (LeafContent dispatcher), nie zmienia struktury modulow.

## Drzewo Modulu

Kazdy modul w `frontend/src/features/<domena>/` albo
`frontend/src/features/editor/modules/<domena>/` ma taki rdzen:

```text
features/<domena>/      albo  features/editor/modules/<domena>/
├── index.ts            # WYMAGANY: publiczne API (barrel selektywny - tylko realnie uzywane)
├── model/              # typy domenowe (types.ts) + czyste funkcje (lib) - bez React/HTTP
├── api/                # hooki danych: useQuery/useMutation (TanStack), queryKeys
├── store/              # Zustand (tylko client state modulu)
├── hooks/              # hooki logiki laczace api+store+model (np. useActiveClip)
├── components/         # React/Konva/Pixi UI modulu
├── <domenowy>/         # dozwolone foldery specyficzne (np. text/render, text/layout)
└── *.test.ts(x)        # testy kolokowane przy testowanym pliku
```

> ⚠️ ELASTYCZNOSC (anti-szkielet): modul ma TYLKO te foldery ktore realnie wypelnia.
> - `page-layers/` = tylko `index.ts` + `api/` + `model/` (czysta infrastruktura danych, bez UI/store).
> - `detection/` = wszystkie foldery (ma overlay Konva, store widocznosci, hooki, czyste funkcje masek).
> NIE tworzymy pustego `store/` "bo szablon ma store". Brak folderu > pusty folder.

Foldery specyficzne dla domeny sa dozwolone, jesli nie staja sie ukrytym shared layerem:
```text
modules/text/
├── layout/             # np. pretextLayout (CJK/bidi) - specyficzne dla tekstu
├── render/             # np. eksport stron, composite - specyficzne dla tekstu
└── style/              # np. mergeRenderStyle - specyficzne dla tekstu
```
Nie dodawaj `modules/_shared.ts` ani cross-module helperow. Kod wspolny dla JEDNEGO modulu zostaje pod
nim. Kod wspolny SYSTEMOWO trafia do `@/lib` (leaf), `@/components/ui` (leaf) albo `@/api` (leaf).

## Przyklad referencyjny (realne moduly w repo)

> Nie wymyslony szablon - to FAKTYCZNA struktura po refaktorze E0-E1.5. Kazdy nowy modul ma wygladac tak.

### `playback/` - modul pelny (silnik odtwarzania wideo)
```text
modules/playback/
├── index.ts                        # API: usePlaybackStore, useActiveClip, usePageAudioPlayback,
│                                   #      useCameraSequence, useVideoSequence, kenBurnsAt, Camera, Timeline
├── model/                          # czyste funkcje + typy (zero React/HTTP)
│   ├── audioSequence.ts  timelineMath.ts  camera.ts  kenBurns.ts  textToPanel.ts
│   └── *.test.ts
├── api/                            # dane serwerowe (TanStack Query)
│   ├── useVideoSequence.ts  useTtsClipsForPage.ts  usePageAudioDurations.ts
│   └── *.test.ts
├── store/usePlaybackStore.ts       # client state (Zustand): playhead, isPlaying, zoom
├── hooks/                          # logika laczaca api+store+model
│   ├── useActiveClip.ts  usePageAudioPlayback.ts  useCameraSequence.ts  useSourcePagePanels.ts
└── components/                     # widok (montowany przez shell)
    └── Timeline.tsx  TimelineClip.tsx  TimelineControls.tsx  TimelinePlayhead.tsx
```

### `page-layers/` - modul minimalny (czysta infrastruktura danych)
```text
modules/page-layers/
├── index.ts                        # API: usePageLayers, useCurrentPageLayer, PageLayer
├── api/                            # usePageLayers.ts  usePageLayerImageElement.ts
├── model/types.ts                  # PageLayer, PageLayerKind
└── hooks/                          # useCurrentPageLayer.ts (selektor)  usePageLayerImageUrl.ts (helper URL)
```
> page-layers NIE ma store/ ani components/ - bo ich nie potrzebuje (anti-szkielet). Ma tylko to co realne.

### Mapa decyzji: gdzie trafia plik?
| Plik robi... | Folder |
|---|---|
| `useQuery`/`useMutation`, fetch, queryKey | `api/` |
| czysta funkcja (matematyka, transform, mapowanie), typ domenowy | `model/` |
| Zustand (client state modulu) | `store/` |
| hook laczacy api+store+model, selektor | `hooks/` |
| React/Konva/Pixi UI | `components/` |
| cos specyficznego dla domeny (np. pretext layout w text) | wlasny folder (`layout/`, `render/`) |
| strona (montowana na trasie) | `components/<x>-page.tsx`, eksport przez barrel |

## Role Plikow

`index.ts` (barrel - API modulu):
- re-eksportuje TYLKO to, co realnie konsumuja inni (sprawdz grep zanim dodasz),
- selektywny, nie `export *` (tree-shaking - patrz typescript.instructions),
- grupuje: hooki z `./api` i `./hooks`, store z `./store`, typy z `./model` (`export type`), UI z `./components`,
- jest JEDYNYM wejsciem do modulu - nikt nie importuje `modules/x/components/Foo` bezposrednio.

`model/`:
- typy domenowe (`types.ts`) + czyste funkcje (matematyka, transformacje, mapowania),
- ZERO React, ZERO HTTP, ZERO Zustand - czysty TS (przenosne, latwo testowalne),
- przyklad: `playback/model/{audioSequence,timelineMath,camera,kenBurns,textToPanel}.ts`.

`api/`:
- hooki danych serwerowych: `useQuery` (read), `useMutation` (write) - TanStack Query 5,
- hierarchiczne queryKeys (`['detection','fusions',runId]`); docelowo z `@/api/keys` factory,
- klient: `@/api/mangashift` (openapi-fetch, typowany). FormData/multipart = raw fetch z `resolveBaseUrl`,
- mutacje: `onSuccess` -> `invalidateQueries`; optimistic z rollback gdy trzeba.

`store/`:
- TYLKO client state modulu (Zustand 5), z selektorami (`useStore(s => s.x)`),
- `persist` tylko gdy uzasadnione (z `version` + `migrate` - patrz pipeline store jako wzor),
- NIE trzymaj tu server state (to nalezy do `api/` + TanStack cache).

`hooks/`:
- hooki logiki laczace api+store+model (np. `useActiveClip` = useVideoSequence + store + timelineMath),
- to "mozg" modulu - orkiestruja, nie fetchuja same (deleguja do api/).

`components/`:
- UI modulu: React, react-konva (image surface), Pixi (video surface),
- ZERO komentarzy (regula frontu), strict typing, cva dla wariantow, cn dla klas warunkowych,
- komponenty biora dane z hooks/store przez API modulu, nie siegaja do wnetrza innych modulow.

## Kontrakt API (barrel)

Minimalny, jawny shape `index.ts` (przyklad - modul `playback`):

```ts
// stan + logika silnika (nie widok)
export { usePlaybackStore } from './store'
export { useActiveClip, usePageAudioPlayback, useCameraSequence } from './hooks'
export { useVideoSequence, useTtsClipsForPage, usePageAudioDurations } from './api'
export type { Camera, ActiveClip, PlaybackState } from './model'
// widok (montowany przez shell)
export { Timeline } from './components'
```

Reguly kontraktu:
1. Inni importuja `from '@/features/editor/modules/playback'` - NIGDY z wnetrza.
2. Zmiana wnetrza modulu NIE moze tlukcic konsumentow (enkapsulacja przez barrel).
3. Co da sie zrozumiec z samego `index.ts` = dobre API. Jak trzeba czytac wnetrze = za szerokie.
4. Eksportuj minimum. Latwiej dodac eksport pozniej niz wycofac (breaking change wewnatrz frontu).

## Stan (gdzie co trzymac)

| Rodzaj stanu | Narzedzie | Gdzie |
|--------------|-----------|-------|
| Server state (dane z backendu) | TanStack Query 5 | `api/` modulu |
| Client state modulu (np. playhead, widocznosc warstw) | Zustand 5 | `store/` modulu |
| Globalny UI (motyw, workspace, kontekst projektu) | Zustand 5 | `@/stores/` - wylacznie ponad-domenowe; stan jednej domeny zyje w `store/` tej domeny |
| Local (form input, hover, drag temp) | `useState` | komponent |

Modul NIE siega do store innego modulu przez `getState()` w ukryciu (dzisiejszy antywzorzec:
mask-paint czyta usePipelineUiStore w mutationFn). Zaleznosc miedzy modulami = jawnie przez barrel API.

## Granica modulu (egzekwowana w CI - E4, caly `src/` w F8)

Modul MOZE importowac:
- `@/lib`, `@/components/ui`, `@/api`, `@/styles` (warstwy leaf),
- `@/stores` (globalne client state),
- INNE moduly TYLKO przez ich `index.ts` (i tylko gdy uzasadnione - cel: moduly niezalezne jak services).

Modul NIE moze:
- importowac wnetrza innego modulu (`modules/y/components/...`) - tylko barrel,
- byc importowany przez warstwe leaf (`@/lib`, `@/components/ui` nie znaja modulow),
- importowac `shell/` ani `canvas/` (zaleznosc idzie: shell/canvas -> modules, nie odwrotnie).

Egzekwowanie: `eslint-plugin-boundaries` (odpowiednik backendowego import-linter). Reguly: leaf nie widzi
modulow; modul->modul tylko przez index; canvas/shell->modul OK; zakaz importu wnetrza. Start `warn` -> `error`.
Fala F8 domknieta: granice objely caly `src/` w trybie **error** (reguly 1-6 nizej), plus
`import-x/no-cycle` (error). Wyjatki TYLKO jawne w `eslint.config.js` z komentarzem "dlaczego"
(zero `eslint-disable` w plikach). Lista aktualnych wyjatkow: `pipeline -> catalog/{model,api}`
deep (cykl wartosci przez barrel; naprawa przy realnej pracy nad panelem ustawien),
`app -> editor-core` (lazy route split - editor/Konva poza glownym chunkiem).

## Canvas Surface (powierzchnia renderu)

`canvas/{image,video}/` to CIENKIE powierzchnie renderu - montuja warstwy z modulow, nie zawieraja ich logiki.
- `canvas/image/` - react-konva surface; montuje overlay'e z detection, mask-paint, text (przez ich barrele).
- `canvas/video/` - Pixi surface (VideoStage); bierze kamere+strone z `modules/playback`.
- `canvas/shared/` - czysta matematyka viewportu (pageFit, viewportMath) - leaf-like, bez modulow.
Surface NIE zna logiki domeny - tylko "co narysowac" (warstwy) i "jak je ulozyc w viewporcie".

## Shell (rama UI)

`shell/` to rama edytora (drzewo splitow, dock, rail, panele-dispatchery). Montuje moduly i powierzchnie.
- `shell/layout/LeafContent` = JEDYNY dispatcher trybow image/video - decyduje co montowac w lisciu.
- Panele (EditorRightPanel, EditorBottomStrip) biora UI z modulow przez barrel.
- Shell zna moduly i canvas; moduly i canvas NIE znaja shell.

## Mapa warstw `src/` (docelowa)

Fale F0-F8 zakonczone 2026-07-09; historia planu w `docs/archive/2026-07/fable_v2/99-plan-fal.md`.

```text
frontend/src/
├── main.tsx                   # bootstrap React (entrypoint z index.html) - ZOSTAJE w korzeniu
├── globals.css                # wejscie CSS
├── test-setup.ts              # setup Vitest (infra)
│
├── app/                       # NOWE: composition root - kod, ktory SKLADA aplikacje
│   ├── app.tsx                # router: trasy -> strony z barreli modulow
│   ├── layout/                # rama okna: topbar, sliding-menu-bar, workspace-tabs,
│   │                          #   workspace-sidebar, status-bar, window-controls, zoom-indicator
│   ├── pill/                  # okno pill (pill-layout, pill-bar) - druga rama okna
│   ├── hooks/                 # hooki startowe: use-backend-health, use-deep-link,
│   │                          #   use-global-hotkeys, use-page-result-invalidation
│   └── navigation.ts          # gotoWorkspace (dawny lib/workspace-navigation)
│
├── api/                       # LEAF transport: mangashift.ts (klient), generated.ts (typy),
│   │                          #   interceptors, errors, sse, job-event-stream, pagination,
│   │                          #   local-token, query-client
│   └── keys.ts                # NOWE: fabryka queryKeys (jedyne zrodlo kluczy cache)
│
├── lib/                       # LEAF czyste helpery: utils(cn), dates, errors, motion,
│                              #   use-now, error-sink, pill-sync (most Tauri)
├── styles/                    # motyw: tokens/theme-dark/theme-light/base/utilities.css
│                              #   + theme-engine.ts (aplikator presetow)
├── components/ui/             # LEAF klocki UI (shadcn + sliding-* + kompozyty) - plasko
├── stores/                    # TYLKO stan PONAD-domenowy: use-app-store,
│                              #   use-project-context-store (nic wiecej)
│
├── features/                  # moduly domenowe wg JEDNEGO ksztaltu (sekcja 1)
│   ├── catalog/               # NOWE: "co jest dostepne" - engines+models+installed z API
│   │                          #   (wchlania dzisiejsze features/models)
│   ├── chapters/              # dane volumes/chapters/pages + drzewo + KLOCEK SCOPE
│   ├── projects/              # projekty + strona startowa + dialog tworzenia
│   ├── pipeline/              # konfiguracja i uruchamianie pipeline + live feed
│   ├── providers/             # klucze API (BYOK)
│   ├── settings/              # karty ustawien + strona ustawien
│   ├── reader/                # stub czytnika (do ksztaltu minimalnego)
│   └── editor/                # JEDYNY modul zlozony (sekcja 4)
│       ├── index.ts           # NOWE: barrel editora (publiczne API dla app/)
│       ├── core/              # entry (editor-workspace), rejestr narzedzi (tools.ts)
│       ├── shell/             # rama edytora: REJESTR PANELI, drzewo splitow, dock, rail
│       ├── canvas/            # powierzchnie renderu: image (Konva), video (Pixi), shared
│       ├── store/             # NOWE: use-editor-store (po rozbiorze god-store)
│       └── modules/           # detection, mask-paint, page-layers, text, playback (bez zmian)
│
├── pages/                     # TYLKO strony deweloperskie: component-gallery, lab
└── test/                      # test-utils (renderWithProviders)
```

## Reguly kierunku zaleznosci

```text
        ┌──────────────────────────────────────────────┐
        │ app/  (composition root - wolno mu wszystko,  │
        │        ale features TYLKO przez barrele)      │
        └───────────────┬──────────────────────────────┘
                        ▼
        ┌──────────────────────────────────────────────┐
        │ features/*  (miedzy soba TYLKO przez index.ts)│
        └───────┬──────────────────────┬───────────────┘
                ▼                      ▼
        ┌──────────────┐      ┌───────────────────────┐
        │ stores/      │      │ leaf: api/ lib/ styles/│
        │ (ponad-dom.) │      │ components/ui/         │
        └──────────────┘      └───────────────────────┘
```

1. **leaf** (`api/`, `lib/`, `styles/`, `components/ui/`) nie importuje `features/`, `stores/`, `app/`.
2. **stores/** nie importuje `features/` ani `app/` (stan ponad-domenowy nie zna domen).
3. **features/** importuja: leaf, stores, INNE features **tylko przez `index.ts`**.
4. **app/** importuje wszystko, ale features **tylko przez `index.ts`**.
5. wewnatrz editora: `shell/canvas/core -> modules`, nigdy odwrotnie; moduly przez barrele.
6. **pages/** (dev) - poza regulami (moze wszystko; nie jest czescia produktu).

## Regula stanu (3 rodzaje)

Kazdy kawalek danych we froncie jest DOKLADNIE jednym z trzech rodzajow. Pomylka rodzaju = zrodlo bugow "dane sie rozjechaly":

| Rodzaj | Co to jest (po ludzku) | Narzedzie | Gdzie mieszka | Przyklady z repo (grep) |
|---|---|---|---|---|
| **server state** | kopia danych, ktorych WLASCICIELEM jest backend (projekty, strony, wyniki detekcji). Front tylko cache'uje | TanStack Query | `api/` modulu (hooki `useQuery`/`useMutation`) | `useProjects` (`['projects','list']`), `useChapterSourcePages` (`['chapters','source-pages',id]`), `useInstalledModels` (`['models','installed']`) |
| **client state** | wybory usera i stan UI, ktorych backend NIE zna (jaki silnik wybrany, uklad paneli, motyw) | Zustand | `store/` modulu; ponad-domenowy w `stores/` | `usePipelineUiStore` (config+runScope, persist `mangashift-pipeline-ui` v1), `useAppStore` (motyw/skala), story modulow editora (detection, mask-paint, playback) |
| **stan lokalny** | efemeryczny stan jednego komponentu (hover, otwarty popover, tryb edycji) | `useState` | wewnatrz komponentu | pozycja pigulki w `sliding-*`, `open` w combobox, tryb edycji `number-scrubber`, drag-preview |

**Regula wlasnosci stanu (egzekwowana w review):**

1. Dane z backendu NIGDY nie mieszkaja w Zustand. Jesli cos ma `id` z API - zyje w TanStack
   (ew. jako parametr w URL). Zustand trzyma tylko WYBORY i UKLAD.
2. Stan jednej domeny zyje w `store/` tej domeny, nie w `stores/`. Globalne `stores/` = tylko
   ponad-domenowe (motyw, workspace, kontekst projektu).
3. Stan, ktory nie musi przezyc odmontowania komponentu, to `useState` - nie store.
4. Kazda invalidacja pisze klucz z `keys.ts` - nigdy literal. `keys.ts` powstaje w F4.

## Przepisy "jak dodac X"

**Narzedzie edytora** (np. nowy pedzel): 1 wpis do `IMAGE_TOOLS` (`core/tools.ts`) -> ikona
pojawia sie w railu. Logika = nowy modul `editor/modules/<narzedzie>/` wg ksztaltu (sekcja 1) +
montaz warstwy w canvas/rejestrze paneli, jesli rysuje. Dotykasz: 1 nowy folder + 1-2 wpisy.

**Panel edytora** (po scaleniu rejestru): 1 wpis do rejestru paneli (id, label, component,
minPx, capabilities) + komponent panelu w module domenowym. Zakladki dostaje za darmo
(stackable). Dotykasz: 1 wpis + 1 komponent.

**Modul app-level** (nowa domena): folder `features/<domena>/` wg ksztaltu + (jesli ma strone)
1 trasa w `app/app.tsx` montujaca strone z barrela. Wzor do skopiowania: `providers/` (maly)
albo `catalog/` (sredni).

**Popup**: uzyj istniejacego kompozytu (ConfirmDialog / Dialog / Sheet / Popover - katalog: 92).
Nowy WZORZEC popupu -> nowy kompozyt w `components/ui/` zbudowany na prymitywie Dialog/AlertDialog.
Nigdy inline-owy dialog w stronie (dzis projects.tsx ma 3 dialogi inline - antyprzyklad).

**Timeline (epik #56)** - test calego fundamentu: timeline = wpis w rejestrze paneli
(panel przesuwalny) + rozbudowa `editor/modules/playback/` (Timeline juz tam zyje: model
timeline-math/ken-burns czysty, store playheadu, komponenty) + klocki: drag-reorder
(do wydzielenia z bottom-strip - 92), generyczny tor/klip. ZERO nowej infrastruktury paneli.

**Klocek UI** (button/scrubber/lista): najpierw grep czy jest w `components/ui/` (katalog: 92).
Jest = uzyj. Nie ma = zbuduj w `components/ui/` sterowany propsami (zero importow stores!).

## Kanon `sliding-*`

**Kanon: warianty `sliding-*` sa DOMYSLNYM wyborem w produkcie.** Pigulka to tozsamosc
wizualna MangaShift (jest w scroll-listach, nav, selectach, menu, tabach - wszedzie, gdzie
user patrzy). Grep to potwierdza: bazowe warianty menu sa w produkcie prawie martwe
(select bazowy 1 uzycie vs sliding-select 4+; context/dropdown bazowe glownie w galerii).

**Ale bazowych plikow NIE kasujemy** - i to nie jest kompromis, tylko architektura:
kazdy `sliding-x` importuje i re-eksportuje bazowy `x` (sliding-tabs -> tabs, sliding-menubar
-> menubar, sliding-command -> command). Bazowy plik = fundament + linia zgodnosci z shadcn
(update shadcn dotyka bazowego, pigulka zyje osobno). Kasacja bazowych zlamalaby sliding-*.

Regula praktyczna:

1. Nowy kod UI siega po wariant `sliding-*`, jesli istnieje dla danej rodziny.
2. Bazowego uzywamy swiadomie tylko tam, gdzie pigulka jest zbedna/szkodliwa
   (gesty chrome edytora, miejsca o wysokiej gestosci interakcji).
3. NIE tworzymy trzeciego wariantu. Potrzebujesz innego zachowania - parametryzuj sliding.

## Sciaga "czego uzyc"

| Potrzebujesz | Bierz |
|---|---|
| przycisk / akcja | `button` (warianty cva) |
| lista przewijana | `sliding-scroll-list` |
| wybor z listy | `sliding-select`; searchable: `combobox` |
| potwierdzenie akcji | `ConfirmDialog` (jedyny kompozyt potwierdzenia; scalenie z confirm-delete w F1) |
| modal z formularzem | `dialog` + kompozycja |
| panel wysuwany | `sheet` |
| zakladki w tresci | `sliding-tabs`; w panelach edytora: `tabs` line (rejestr paneli) |
| wiersz ustawienia | `setting-row`; z suwakiem: `slider-row`; z labelem: `form-field` |
| wiersz listy z akcjami | `list-item` |
| liczba przeciagana | `number-scrubber` z `ui/` (warianty field/inline po F1) |
| pusty stan / ladowanie | `empty-state` / `skeleton` / `spinner` / `loading-bar` |
| toast | `sonner` (montowany w app/) |
| menu kontekstowe / dropdown / menubar | `sliding-context-menu` / `sliding-dropdown-menu` / `sliding-menubar` |

Nie ma na liscie? Grep w `components/ui/` -> jest: uzyj; nie ma: zbuduj w `ui/` sterowane
propsami (zero stores) i dopisz do galerii.

## Typowanie i styl

Obowiazuje [typescript.instructions](../../.claude/skills/instructions/references/typescript.instructions.md):
- TS strict, zero `any`, `unknown` + narrowing,
- `type` > `interface`, discriminated unions, `as const`, `satisfies`,
- naming: komponenty PascalCase, hooki `use*`, foldery kebab-case, stale SCREAMING_SNAKE,
- ZERO komentarzy w kodzie frontu (kod tlumaczy sie sam) - JSDoc tylko dla publicznego API w `@/components/ui`,
- barrel OSTROZNIE (selektywny, nie `export *` - tree-shaking).

## Testy wymagane

- czyste funkcje w `model/` - unit (Vitest), ~100% (np. `audioSequence.test.ts`, `timelineMath.test.ts`),
- hooki - `renderHook` + wrapper (QueryClient), happy path,
- komponenty kluczowe - RTL (getByRole > getByTestId),
- testy kolokowane przy pliku (`Foo.test.tsx` obok `Foo.tsx`),
- po E4: test ze ESLint boundaries lapie sztuczne naruszenie granicy.

## Definition of Done (modul)

Modul jest "100/100" gdy:
1. Ma `index.ts` z MINIMALNYM, jawnym API (rozumiesz "co robi" bez czytania wnetrza).
2. Wnetrze niewidoczne dla innych (importy tylko przez barrel).
3. Da sie zmienic wnetrze bez tlukcenia konsumentow.
4. Zaleznosci wychodzace: tylko leaf + globalne stores + inne moduly przez barrel.
5. ZERO pustych folderow - kazdy podfolder ma realna zawartosc.
6. Stan we wlasciwej warstwie (server=api/TanStack, client=store/Zustand, local=useState).
7. Testy kolokowane, zielone. `bun run typecheck && lint && build && test` GREEN.
8. Dodanie pokrewnego ficzera = zmiana w TYM module, nie w innych.

Gdy nowy ficzer nie pasuje do zadnego modulu -> ZAKLADAMY NOWY modul (jak nowy service backendu).
Nie dolepiamy "bo blisko". Nie tworzymy pustego modulu "na przyszlosc" (anti-szkielet).
