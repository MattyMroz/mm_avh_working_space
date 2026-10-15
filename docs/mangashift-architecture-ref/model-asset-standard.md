# Model Asset Standard v4

Standard granicy między model catalog, physical cache i engine code. Cel: jeden source of truth dla nazw plików, hashy, formatów i resource roots.

> **v4 (2026-07-05, FALA 8):** `ModelFactory` (`runtime/factory.py`) skasowany razem z
> `ModelSpec.default_config`/`RESERVED_KEYS` (katalog nigdy nie miał defaultów silnika osobno
> od modelu - teraz nie ma pola z parametrami silnika w ogóle). `model_id` przychodzi na
> configu domeny (od frontu) i idzie na config silnika przez `create_engine(config)` (rejestr
> domeny, `services/<domena>/engines/__init__.py`), nie przez wstrzyknięcie z factory.
>
> **v3 (2026-07-04):** epik "serwer=wykonawca, front decyduje" - `variant` skasowany jako
> byt; `model_id` jedynym selektorem, WYMAGANY na configu silnika. Katalog odpowiada JAK
> dociągnąć pliki dla danego `model_id`; KTÓRY `model_id` w danym wywołaniu decyduje front
> (request), nie katalog i nie silnik.
>
> **v2 (2026-07-02):** ujednolicone nazewnictwo bytów. Engine wybiera asset przez `model_id`
> (albo jawnie `resource_name`, gdy adresuje współdzielony bundle) - nie przez fizyczne
> filenames. Słownik i granice: **[naming-glossary.md](naming-glossary.md)**.

## Source Of Truth

Nazwy bytów (`model_id`, `resource_name`, `engine_id`) wg [naming-glossary.md](naming-glossary.md).
`variant` jest bytem skasowanym - `model_id` jedynym selektorem modelu.

| Warstwa | Może trzymać | Nie może trzymać |
|---|---|---|
| `external/models` | fizyczne pliki cache | decyzji runtime ani defaultów produkcyjnych |
| `mangashift/models/catalog.py` | `resource_name`, per-format asset paths, hashes, sizes, HF metadata, production format | engine algorithm constants, decyzji „który `model_id`" (to robi front) |
| `mangashift/models/resolver.py` | resolution/download/check integrity (mapuje `model_id`/`resource_name` → fizyczny bundle) | domain-specific preprocessing |
| `services/*/engines/*/constants.py` | algorithm constants, labels, thresholds, allow-listę `model_id → cecha` (dla 1:N) | physical filenames, asset paths, hashes, `resource_name` jako ścieżka |
| `services/*/engines/*/config.py` | runtime choices, backend, device, wymagane pole `model_id` (przekazane przez `create_engine`) | HF paths, sha256, cache layout |
| `services/*/engines/*/service.py` | pyta resolver o asset po `model_id` | path concatenation with hardcoded filenames |

Katalog odpowiada JAK dociągnąć pliki dla `model_id` (assety, hashe, formaty); KTÓRY `model_id`
w danym wywołaniu - decyduje front (request), nie katalog i nie silnik. `ModelSpec` nie ma pola
z domyślnymi parametrami silnika (dawny `default_config`/`RESERVED_KEYS` skasowane razem z
`ModelFactory`, FALA 8) - katalog trzyma wyłącznie `model_id`/`engine_family`/`resource`/klasy
rozmiaru, zero decyzji wyboru silnika czy parametrów runtime.

## Catalog Contract

Each model resource in [mangashift/models/catalog.py](../mangashift/models/catalog.py) should declare assets by artifact format:

```python
_resource(
    "resource-name",
    "onnx",
    _asset("pt", _file("pt/model.pt", ...)),
    _asset("onnx", _file("onnx/model.onnx", ...)),
)
```

Rules:

- asset file paths are relative to the resource directory,
- path separators are `/`, never `\\`,
- paths are not absolute,
- paths never contain `..`,
- first path segment normally equals the artifact format (`pt/`, `onnx/`, `gguf/`, `native/`, `comfy/`), unless a documented legacy bundle requires otherwise.

`ModelSpec` has no field carrying default engine parameters (the old `default_config` /
`RESERVED_KEYS` guard was removed together with `ModelFactory`, FALA 8) - the catalog never
held selection decisions (`engine`, `engine_id`, `backend`, `variant`, `model_id`), only model
traits, and now it doesn't hold engine parameters at all. The real mechanism for picking an
artifact/runtime lives on `ModelSpec` itself:

- `default_artifact_format: ArtifactFormat | None` - explicit pin for the default artifact,
- `runtime: RuntimeKind | None` - explicit override of the execution runtime,
- `dev_artifact_format: ArtifactFormat | None` - artifact chosen when a pipeline profile runs in dev/lab mode,
- `spec.execution_target(artifact_format=...) -> ExecutionTarget | None` (`mangashift/models/specs.py`) resolves the artifact/runtime pair, falling back through `effective_artifact_format` → first asset format on `resource` → `None`.

## Engine Contract

Engine wybiera asset po **tożsamości semantycznej** (`model_id`), nie po fizycznych nazwach plików.
`model_id` jest polem WYMAGANYM na configu silnika, przekazywanym przez `create_engine(config)`
(rejestr domeny, `services/<domena>/engines/__init__.py`) z configu domeny (od frontu) - nie
wyprowadzanym z `variant` (byt skasowany), zarówno dla engine 1:N jak i dla degeneratu 1:1:

```python
resolved = resolve_model_asset(
    model_id=self.config.model_id,      # np. "hi_sam_h" - z configu domeny, od frontu
    artifact_format=self.config.artifact_format,
)
```

Selektor = `model_id`. `resource_name` (kebab, np. `hi-sam`) jest szczegółem, który resolver
sam mapuje - engine go nie podaje jako ścieżki. Wyjątek: engine celowo adresuje współdzielony
bundle po `resource_name` (rzadkie) - wtedy jawnie, jako argument nazwany, nie przez sklejanie ścieżek.

Zakazane - wybór modelu przez fizyczną nazwę pliku:

```python
path = ensure_model(RESOURCE_NAME) / MODEL_FILENAME   # ANTYWZORZEC
```

`resolver.ensure_model_asset()` przyjmuje selektor semantyczny; nowy kod nie skleja ścieżek
z hardcoded filenames. Compatibility wrappers mogą zostać podczas migracji, ale nowy kod idzie przez catalog assets.

## Forbidden Engine Constants

These names are forbidden in engine `constants.py` once migration debt is paid:

- `MODEL_FILENAME`
- `ONNX_FILENAME`
- `PT_FILENAME`
- `PT_ASSET_PATH`
- `ONNX_ASSET_PATH`
- any `*_SHA256`
- any `*_HF_PATH`

Use catalog resource assets instead.

## External Models Contract

`external/models` is a cache mirror, not a policy layer.

Rules:

- one canonical directory per catalog resource root,
- legacy aliases are not allowed for canonicalized resources,
- duplicate roots must be removed or treated as orphan cache,
- tests should detect orphan roots and catalog roots with no on-disk mirror when the local cache is expected to be complete.

Canonical Magi v3 naming (byty rozdzielone - patrz [naming-glossary.md](naming-glossary.md)):

- `resource_name` (bundle, kebab): `magi-v3` → root `external/models/detection/magi-v3/`
- `engine_id` (silnik, snake): `magi_v3`
- `model_id` (wpis katalogu, snake): `magi_v3`
- aliases: none; `magiv3` i `magi` nie są nazwami kompatybilnymi

> Magi to degenerat 1:1:1 (`engine_id == model_id`, `resource_name` = kebab tego samego).
> To szczególny przypadek, NIE wzorzec - nie uogólniaj „engine/model id to jedno". Dla
> silników 1:N (`hi_sam` → `hi_sam_{b,l,h}`) te byty są różne.

## Migration Order

1. Add catalog assets for every format that engines need.
2. Add/extend resolver API returning a format-specific resolved asset.
3. Replace engine path concatenation with resolver calls.
4. Remove physical filename constants from engines.
5. Shrink invariant test allowlists.

## Enforcement

Current tests:

- [tests/models/test_catalog_service_contract.py](../tests/models/test_catalog_service_contract.py)
- [tests/services/test_engine_structure_invariants.py](../tests/services/test_engine_structure_invariants.py)

The current tests block new drift and document existing debt. They are not a substitute for the next migration wave.