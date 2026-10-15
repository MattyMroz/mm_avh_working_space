# Audyt 07 — Binarki `.exe` vs biblioteki Pythona

> Decyzja architektoniczna: czy da się zredukować zależność od binarek w folderze `bin/`,
> zastępując wywołania `subprocess` natywnymi bibliotekami Pythona.
> Stan wiedzy: lipiec 2026. Projekt: `mm_avh_working_space` (CLI Windows, anime → lektor).

---

## TL;DR

- **ffmpeg/ffprobe** — TAK, da się zastąpić natywnie przez **PyAV** (wbudowany FFmpeg w wheelu, bez `.exe`), ale z jednym haczykiem: PyPI-owe wheele PyAV są LGPL i **nie mają `libx264`**, którego używa ścieżka „Wypal do mp4". eac3, mp3, atempo, probe — działają.
- **balcon/balabolka** — TAK, częściowo już zastąpione. Projekt **już importuje `pyttsx3`** (ścieżka Harpo). `pyttsx3` to natywny SAPI5 — teoretycznie zastąpi balcon, ale głos „IVONA 2 Agnieszka" i jakość/tempo mogą się różnić.
- **mkvtoolnix** (mkvextract/mkvmerge/mkvinfo) — **NIE**. Nie istnieje dojrzała, natywna biblioteka Pythona, która ekstrahuje i muxuje ścieżki MKV bez `.exe`. Wszystkie realne opcje (`pymkv2`) i tak wołają `mkvmerge.exe`. To serce pipeline i **musi zostać jako `.exe`**.
- **espeak-ng** — w kodzie Pythona **nie jest w ogóle wywoływany** (tylko martwa stała ścieżki w `constants.py`). Nic do migracji.

---

## Tabela zbiorcza

| Binarka | Do czego w projekcie | Biblioteka-kandydat | Natywne czy owija `.exe`? | Dojrzałość | Rekomendacja |
|---|---|---|---|---|---|
| **mkvextract.exe** | ekstrakcja ścieżek audio/napisów z MKV | `pymkv2` (mux only), `python-matroska` (demux+mux) | pymkv2 = owija `.exe`; python-matroska = natywne | pymkv2: 29★, żywy; python-matroska: 4★, 0 releasów | **ZOSTAŃ przy `.exe`** |
| **mkvmerge.exe** | merge audio+wideo+napisy do MKV, także `--identify` (info) | `pymkv2` | owija `mkvmerge.exe` (wymaga go w systemie) | 29★, v2.3.2 (maj 2026), Py 3.10–3.14 | **ZOSTAŃ przy `.exe`** (ewent. cienki wrapper) |
| **mkvinfo.exe** | *(nieużywane — info robi `mkvmerge --identify`)* | `Ravencentric/mkvinfo`, `enzyme` | owija mkvmerge / natywny reader | niszowe | **ZOSTAŃ** (i tak potrzebny mkvmerge) |
| **mkvpropedit.exe** | *(importowany, ale w kodzie niewywoływany)* | — | — | — | **USUŃ z zależności** jeśli faktycznie martwy |
| **ffmpeg.exe** | eac3↔mp3/wav, atempo (tempo), amix, volume, burn napisów, RF64>4GB | **PyAV (`av`)**, `imageio-ffmpeg`, `static-ffmpeg`, `pydub` (już jest) | PyAV = **natywne, bundled FFmpeg**; reszta = owija `.exe` | PyAV 3.2k★, v18.0.0 (lip 2026), Py 3.11–3.14, wheele Win x64+ARM64 | **HYBRYDA / PRZEJDŹ** (uwaga na libx264) |
| **ffprobe.exe** | długość audio (`pydub.mediainfo`) | PyAV (`av.open().duration`), `soundfile` | natywne | dojrzałe | **PRZEJDŹ** (PyAV/soundfile) |
| **balcon.exe** | TTS lektor „IVONA 2 Agnieszka" (SAPI) | **`pyttsx3`** (już w projekcie!), `pyttsx4`, `win32com SAPI.SpVoice` | natywne (SAPI5 przez COM) | pyttsx3 żywy, popularny; SAPI natywny Win | **HYBRYDA** (test jakości głosu) |
| **espeak-ng** | *(tylko stała ścieżki — niewywoływane)* | `py-espeak-ng`, `phonemizer` | wrappery ctypes na `libespeak-ng` | średnia, Linux-first | **USUŃ** martwą stałą |

---

## Per binarka — uzasadnienie + pakiet pip

### mkvextract / mkvmerge / mkvinfo (MKVToolNix) — ZOSTAŃ przy `.exe`

To jest sedno pytania i odpowiedź jest jednoznaczna: **nie ma pełnowartościowego natywnego zamiennika.**

- **`pymkv2`** (`pip install pymkv2`, v2.3.2, maj 2026, Py 3.10–3.14) to najżywszy wrapper, ale to nadal **wrapper na `mkvmerge.exe`** — jego własna dokumentacja mówi wprost „mkvmerge must be installed on your computer". Skupia się na muxowaniu (łączeniu); **ekstrakcji (`mkvextract`) praktycznie nie eksponuje**. Czyli: więcej ładnego API, zero mniej `.exe`.
- **`python-matroska`** (shersonb) to jedyny projekt robiący demux+mux **natywnie w Pythonie**, ale ma **4 gwiazdki, zero wydań na GitHub/PyPI** i status „dojrzewający, nie produkcyjny". Wrzucanie serca pipeline (ekstrakcja + merge finalnego pliku dla usera) na taki fundament to proszenie się o edge case'y z kontenerami MKV (rozdziały, tagi, attachmenty, kolejność ścieżek, opóźnienia).
- `enzyme` / `mkvparse` / `Ravencentric/mkvinfo` — tylko **czytają metadane**, nie ekstrahują ani nie muxują.

Projekt używa też `mkvmerge --identify --identification-format json` do pobrania info o ścieżkach — to i tak wymaga `mkvmerge.exe`, więc nawet „info" nie da się oderwać od binarki.

**Werdykt:** `mkvextract.exe` + `mkvmerge.exe` **muszą zostać**. Ewentualne ulepszenie kosmetyczne: owinąć wywołania w `pymkv2` dla czytelniejszego API merge — ale to NIE usuwa binarki, tylko dokłada zależność. Nie warto.

`mkvinfo.exe` i `mkvpropedit.exe` są w `constants.py`, ale w kodzie **nieużywane** (info robi `mkvmerge --identify`, propedit nigdzie nie wołany). Można je usunąć z listy sprawdzanych plików i ewentualnie z `bin/`.

---

### ffmpeg / ffprobe — HYBRYDA / PRZEJDŹ na PyAV (z zastrzeżeniem)

**`pip install av`** (PyAV, v18.0.0, lip 2026, 3.2k★, wheele Windows x64 + ARM64 dla Py 3.11–3.14).

PyAV to **natywne bindingi do bibliotek libav* FFmpeg** — wheele z PyPI **mają wbudowany FFmpeg**, więc **`ffmpeg.exe` przestaje być potrzebny**. To jedyny kandydat, który realnie usuwa binarkę (pydub, imageio-ffmpeg, static-ffmpeg to wszystko wrappery/dostawcy `.exe`).

Co z operacji projektu PyAV zrobi natywnie:
- **eac3 ↔ mp3/wav** — TAK. `eac3` i natywny enkoder `mp3` (a także `libmp3lame`) są w standardowym FFmpeg i w LGPL-owym wheelu PyAV.
- **atempo (zmiana tempa)** — TAK, przez graf filtrów (`av.filter`). To pokrywa cały `_build_atempo_chain` i `_pp_speed_*`.
- **amix + volume (miks lektor+oryginał, +7dB)** — TAK, filtry `amix`/`volume` są wbudowane.
- **długość audio (zamiast ffprobe)** — TAK, `container.duration` / dekodowanie; alternatywnie `soundfile` (już w projekcie przy ElevenBytes).
- **RF64 / WAV > 4GB** — do sprawdzenia w praktyce; obecny kod świadomie używa `-rf64 auto`. Muxer WAV FFmpeg to obsługuje, ale trzeba zweryfikować przez API PyAV.

**HACZYK — ścieżka „Wypal do mp4" (`mkv_burn_to_mp4`) używa `libx264`** (`-c:v libx264`) oraz filtra `subtitles=`. **`libx264` jest GPL i NIE MA go w LGPL-owych wheelach PyAV z PyPI.** Próba enkodowania H.264 przez PyAV z PyPI skończy się „unknown encoder libx264". To znaczy:
- Ścieżki **audio** (lektor: eac3, mp3, atempo, amix, probe) → **PyAV pokrywa w 100%**.
- Ścieżka **wideo „wypal do mp4"** → PyAV z PyPI **nie zastąpi** (brak x264; filtr `subtitles` wymaga libass wkompilowanego). Tu `ffmpeg.exe` musiałby zostać albo trzeba by własnego wheela FFmpeg z GPL/OpenH264.

**Werdykt:** **HYBRYDA.** Przenieś na PyAV cały tor audio lektora (to większość wywołań ffmpeg w projekcie: `_convert_to_eac3`, `_merge_files`, `_pp_speed_*`, `_atempo_pipe`, probe długości). **Zostaw `ffmpeg.exe` tylko dla „wypal do mp4"** (x264 + burn napisów) — albo zaakceptuj, że ta jedna funkcja dalej potrzebuje binarki. Realnie usuwasz ~90% wywołań ffmpeg, ale binarka zostaje dla 1 opcji wideo.

> Uwaga: `pydub` (już w projekcie) i `mediainfo`/`ffprobe` również można wyprzeć przez PyAV/soundfile, co pozwoliłoby usunąć konfigurację `AudioSegment.converter/ffmpeg/ffprobe` z `constants.py`.

---

### balcon / balabolka (SAPI TTS) — HYBRYDA (przetestuj jakość)

**`pip install pyttsx3`** — **projekt już go importuje i używa** w ścieżce „TTS - Zosia - Harpo" (`_init_engine`, `save_to_file`). Na Windows `pyttsx3` korzysta z **SAPI5** przez COM — dokładnie z tego samego API mowy Windows, którego używa `balcon`. Alternatywy: `pyttsx4` (fork z nowszymi featami), bezpośrednio `win32com.client` → `SAPI.SpVoice` (pełna kontrola, zapis do WAV przez `SpFileStream`).

Skoro balcon i pyttsx3 sięgają do tego samego silnika SAPI, **te same głosy są dostępne** (m.in. „IVONA 2 Agnieszka", jeśli zainstalowana w systemie). pyttsx3 potrafi ustawić `voice`, `rate`, `volume` i `save_to_file` → WAV. Czyli funkcjonalnie **da się zastąpić balcon**.

Zastrzeżenia (dlaczego HYBRYDA, nie twarde „PRZEJDŹ"):
- balcon ma bogatsze sterowanie prozodią/pauzami i parametr `-fr 48` (framerate) oraz precyzyjne mapowanie tempa; pyttsx3 `rate` to inna skala — **wynik brzmieniowy może się różnić**, trzeba porównać na uchu.
- **Polskie znaki**: balcon świadomie robi konwersję na ANSI (`ansi_srt`) przed syntezą — pyttsx3 przyjmuje `str` (Unicode), więc teoretycznie problem znika, ALE to trzeba zweryfikować dla konkretnego głosu IVONA (część starych głosów SAPI ma problemy z Unicode i wymaga code page).
- pyttsx3 bywa kapryśny przy `save_to_file` w pętli (znane problemy z `runAndWait` na Windows) — projekt już to obchodzi w torze Harpo, więc wzorzec jest znany.

**Werdykt:** kandydat realny i **już częściowo wdrożony**. Rekomendacja: dorobić ścieżkę TTS opartą wyłącznie na pyttsx3/SAPI jako opcję i **porównać jakość/tempo z balcon na próbce z polskimi znakami**. Jeśli brzmi tak samo → można wyrzucić `balcon.exe`. Do czasu weryfikacji jakości: hybryda.

---

### espeak-ng — USUŃ martwą stałą

W kodzie Pythona **nie ma ani jednego wywołania espeak-ng** — jest tylko stała `ESPEAK_NG_FOLDER` w `constants.py`, do niczego niepodpięta. Gdyby kiedyś była potrzebna synteza/fonemy: **`pip install py-espeak-ng`** (ctypes na `libespeak-ng`, natywne, bez `.exe`) lub `phonemizer`. Oba są Linux-first i średnio utrzymywane; na Windows wymagają DLL espeak-ng.

**Werdykt:** nic do migracji. Jeśli `bin/espeak-ng` i stała są faktycznie nieużywane → **usunąć** (redukcja zależności za darmo).

---

## Sekcja „1 plik, 1 zależność" — do ilu realnie da się zredukować binarki

Stan obecny w `bin/`: **mkvtoolnix (4 exe) + ffmpeg (2 exe) + balabolka (balcon) + espeak-ng** — realnie ~4 grupy binarne.

Co da się zdjąć:

| Binarka | Da się usunąć? | Czym |
|---|---|---|
| espeak-ng | **TAK** (jest martwa) | nic — usunąć stałą/folder |
| mkvinfo.exe | **TAK** (nieużywana) | `mkvmerge --identify` już to robi |
| mkvpropedit.exe | **TAK** (nieużywana) | — |
| ffprobe.exe | **TAK** | PyAV / soundfile |
| ffmpeg.exe (tor audio) | **TAK** (~90% użyć) | PyAV (eac3/mp3/atempo/amix/volume/probe) |
| ffmpeg.exe (wypal do mp4) | **NIE** (x264 GPL) | zostaje dla 1 opcji wideo, lub własny wheel FFmpeg |
| balcon.exe | **PRAWDOPODOBNIE** (po teście jakości) | pyttsx3 (SAPI5, już w projekcie) |
| mkvextract.exe | **NIE** | brak dojrzałego natywnego zamiennika |
| mkvmerge.exe | **NIE** | jw. (`pymkv2` i tak go wymaga) |

**Realna redukcja:**
- **Łatwo i od razu:** usuń espeak-ng, mkvinfo, mkvpropedit (martwe) → z „4 grup" psychologicznie robi się czyściej, choć to i tak pliki obok mkvmerge.
- **Średnio (warto):** przenieś tor audio na PyAV → **ffprobe znika w całości**, ffmpeg zostaje tylko dla „wypal do mp4".
- **Po weryfikacji jakości:** balcon → pyttsx3 → balabolka znika.

**Twarde minimum, którego NIE zejdziesz:** **`mkvextract.exe` + `mkvmerge.exe`** (MKVToolNix). To jedyna nieusuwalna zależność binarna — ekstrakcja ścieżek z MKV i budowa finalnego MKV dla usera. Plus opcjonalnie `ffmpeg.exe`, jeśli chcesz zachować „wypal do mp4" z x264.

**Najbardziej realistyczny cel: z ~4 grup binarnych → 1 obowiązkowa (MKVToolNix) + 1 opcjonalna (ffmpeg tylko dla mp4-burn).**

---

## Ryzyka przejścia

**PyAV (ffmpeg):**
- **libx264 brak w LGPL wheelu** — „wypal do mp4" nie zadziała przez PyAV z PyPI. Trzeba zostawić ffmpeg.exe albo zbudować własny wheel (koszt utrzymania).
- **Filtr `subtitles=` (burn napisów)** wymaga libass wkompilowanego w FFmpeg — w standardowym wheelu PyAV może go nie być. Kolejny powód, by burn zostawić na `.exe`.
- **RF64 / WAV > 4GB** — obecny kod celowo używa `-rf64 auto`. Trzeba potwierdzić, że muxer WAV przez PyAV zapisze poprawny RF64 dla wielogodzinnego lektora, inaczej regresja (crash na >4GB).
- **Zmiana dekodera/resamplera** — bit-nieidentyczny wynik vs obecny ffmpeg.exe (kod już to zauważa przy soundfile). Kosmetyka, ale warto wiedzieć.
- **Krzywa uczenia API filtrów** — graf filtrów PyAV jest bardziej rozwlekły niż string `-af "atempo=..."`; więcej kodu do napisania i przetestowania.

**pyttsx3 (balcon):**
- **Brzmienie/tempo IVONA Agnieszka** może odbiegać od balcon (inna skala `rate`, inna prozodia) — subiektywna regresja jakości lektora.
- **Polskie znaki w starych głosach SAPI** — ryzyko krzaków, jeśli głos oczekuje konkretnego code page; balcon+ANSI to dziś obchodzi. Konieczny test na próbce z „ą, ę, ł, ó, ż, ź, ś, ć, ń".
- **`runAndWait` / `save_to_file` w pętli** na Windows bywa niestabilne (znane zawieszki) — wymaga tego samego ostrożnego wzorca co istniejąca ścieżka Harpo.
- **Zależność od głosów zainstalowanych w systemie** — dokładnie jak balcon, więc bez regresji, ale nadal nie „portable".

**mkvtoolnix (gdyby jednak próbować python-matroska):**
- 4★, 0 wydań — **niedojrzałe**. Edge case'y kontenerów MKV: rozdziały, tagi, attachmenty (czcionki dla ASS!), opóźnienia ścieżek, dziwne kodeki, kolejność/domyślność ścieżek. Wysokie ryzyko cichego zepsucia finalnego pliku, który dostaje user. **Odradzam.**

**Ogólne:**
- Każda migracja to **nowa powierzchnia testów** dla całego pipeline (ekstrakcja → TTS → merge). Przy sercu MKV ryzyko > korzyść.
- Zysk „portable bez .exe" jest częściowy: MKVToolNix i tak zostaje, więc projekt **nigdy nie będzie w 100% wolny od binarek**. Warto to przyjąć jako fakt architektoniczny.

---

## Rekomendacja końcowa (priorytety)

1. **Za darmo, teraz:** usuń martwe zależności — `espeak-ng`, `mkvinfo`, `mkvpropedit` (nieużywane w kodzie).
2. **Warto (audio):** przenieś tor audio lektora na **PyAV** → usuwasz `ffprobe.exe` i ~90% wywołań `ffmpeg.exe`. Zostaw `ffmpeg.exe` tylko dla „wypal do mp4".
3. **Po teście jakości:** rozważ **pyttsx3** zamiast `balcon.exe` (już masz pyttsx3) — decyzja po odsłuchu polskiej próbki.
4. **Nie ruszaj:** `mkvextract.exe` + `mkvmerge.exe` — zostają jako `.exe`, brak dojrzałego natywnego zamiennika.

---

## Źródła

- [pymkv2 — PyPI](https://pypi.org/project/pymkv2/) / [GitHub GitBib/pymkv2](https://github.com/GitBib/pymkv2)
- [python-matroska — GitHub shersonb](https://github.com/shersonb/python-matroska)
- [enzyme — PyPI](https://pypi.org/project/enzyme/) / [mkvparse](https://github.com/vi/mkvparse) / [Ravencentric/mkvinfo](https://github.com/Ravencentric/mkvinfo)
- [PyAV (av) — PyPI](https://pypi.org/project/av/) / [GitHub PyAV-Org/PyAV](https://github.com/pyav-org/pyav) / [Audio cookbook](https://pyav.basswood-io.com/docs/stable/cookbook/audio.html)
- [BtbN/FFmpeg-Builds — konfiguracje GPL/LGPL](https://github.com/BtbN/FFmpeg-Builds) / [Prebuilt LGPL FFmpeg + OpenH264](https://github.com/Crigges/Prebuilt-LGPL-2.1-FFmpeg-with-OpenH264)
- [pyttsx3 — PyPI](https://pypi.org/project/pyttsx3/) / [GitHub nateshmbhat/pyttsx3](https://github.com/nateshmbhat/pyttsx3) / [pyttsx4](https://pypi.org/project/pyttsx4/)
- [Balabolka Console (balcon) — dokumentacja](https://www.cross-plus-a.com/bconsole.htm)
- [py-espeak-ng — GitHub gooofy](https://github.com/gooofy/py-espeak-ng) / [phonemizer / espeak-phonemizer-windows](https://pypi.org/project/espeak-phonemizer-windows/)
