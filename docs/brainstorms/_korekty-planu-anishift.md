# korekty do planu AniShift (2026-07-12, po recenzji usera)

Plan bazowy: `2026-07-12-plan-anishift-fable-v2.md` — ZATWIERDZONY z poniższymi korektami.

## workspace/ — UPROSZCZONY (user: "wszystko ma być proste")
- User wrzuca MKV do `workspace/`, pliki pośrednie (napisy .srt, .eac3) powstają OBOK wrzuconych plików — jak dziś ("zapisujesz w samym workspace dodatkowe pliki np napisów czy eac3").
- Podfoldery: TYLKO `tmp/` (robocze) + `output/` (wyniki). Reszta z planu Fabla (input/, cache/, logs/, settings.json w workspace) — WYLATUJE.
- **output/ = OPCJA w /settings**: ustawienie "przenieś gotowe wyniki do output/" TAK/NIE. Domyślnie pliki zostają w workspace obok MKV; jeśli włączone — gotowe (mp4/mkv) lądują w output/. To kwestia ustawienia, nie sztywna struktura.
- Sam output może być: wypalone mp4 ALBO złożony 1 plik mkv (jak dziś, tryby wyjścia).

## co WYLATUJE z workspace (NIE ma tam być)
- **settings.json** — NIE w workspace. Idzie gdzie indziej (config obok kodu / APPDATA — do dobrania w implementacji, byle nie w workspace). Odstępstwo Fabla #1 (settings w workspace) ODRZUCONE.
- **logi — DOMYŚLNIE WYŁĄCZONE.** Zero logs/. ("logi domyślne wyłączone").
- **cache — WYWALONE.** Zero osobnego cache/. Jeśli elevenbytes potrzebuje wznowienia po crashu (drogie API, nie powtarzać opłaconych requestów) — trzyma to SAM w tmp/, nie w osobnym folderze cache/. ("cache co ma być w cache? nie rozdmuchujemy wszystko ma być proste").

## odstępstwa Fabla od MangaShift (F.7) — decyzje usera
- (a) settings.json w workspace → **ODRZUCONE** (settings wylatuje z workspace, patrz wyżej).
- (b) Typer na wejściu → **ZOSTAJE** (daje doctor/setup za darmo).
- (c) pydantic-settings dla .env → **ZOSTAJE**.

## POMYSŁ NA PRZYSZŁOŚĆ (notatka, NIE teraz)
- Auto-pobieranie anime z internetu: wrzucasz nazwę anime → program sam ściąga (torrent lub inne rozwiązanie). User: "funkcja automatycznego pobierania, wyrażnie anime jest dosłownie z internetu za pomocą jakiegoś rozwiązania np bittorrent". NIE rozstrzygamy teraz — pomysł na później, po przebudowie.

## reszta planu Fabla v2 — bez zmian
- Recykling MangaShift (services/<domena>/engines/, bootstrap, doctor, factory-standard) ✅
- external/bin/ + bin_hashes.json ✅
- ffmpeg=.exe, mkvtoolnix=.exe, balcon=.exe Windows-only przez is_available() ✅
- silniki: tts=elevenbytes/edge/harpo/balcon, translation=google/deepl ✅
- 7 etapów, stary kod żyje do etapu 7 ✅
- nazwa AniShift / anishift ✅
