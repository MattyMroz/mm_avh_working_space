# poprawki do planu — RUNDA 2 (2026-07-12, wieczór)

User odrzucił OBA plany (Sol + Fable). Do jutra — poprawić prompt do Fabla i odpalić jeszcze raz.

## dlaczego oba plany są złe (moja wina — zły prompt do Fabla/Sola)

1. **OBA używają starego nazewnictwa AI i starych wzorców** — "oba plany do wypierdolenia".
2. **Kazałem CAŁKIEM NOWE repo/projekt** — a Fable zbudował WŁASNĄ nową architekturę zamiast
   **RECYKLINGU W 100% SERWISÓW Z MANGASHIFT**. Fable dodał fajne pliki, ALE usunął to co w
   MangaShift było NAJMOCNIEJSZE. To błąd.
3. **`working_space` NIE ISTNIEJE w nowej wizji.** Ma być **`workspace`** (jak MangaShift), NIE
   `working_space`. Fable skopiował głupi błąd/przekonanie z OBECNEGO repo zamiast wziąć wzorzec
   MangaShift.
4. **Struktura ma być jak MangaShift:** `external/bin`, `workspace` (nie working_space), itd.
   Mówiłem to wyraźnie, plan to zignorował.

## czego user chce NAPRAWDĘ (na jutro)

- **NOWE repo/projekt** — inna nazwa niż mm_avh_working_space (do ustalenia jutro).
  Rozważane: nowe repo na GitHubie. ALE obecne ma 3 gwiazdki ;( — więc może jednak zostać obecne
  repo (do decyzji). "może jednak nie to zmieniamy bo ma małe ale 3 gwiazdki".
- **Recykling serwisów z MangaShift w 100%** — wziąć NAJMOCNIEJSZE wzorce MangaShift (services/,
  engine registry, struktura external/bin + workspace), NIE wymyślać nowej architektury od zera.
- **Nazewnictwo z MangaShift:** external/bin, workspace (NIE working_space), engine standardy.
- Fable ma się ZREFLEKTOWAĆ i poprawić plan.

## pytania do Fabla na jutro (user chce żeby Fable sam to rozważył)

1. **ffmpeg — biblioteka pythonowa czy .exe?** To jest PYTANIE (nie przesądzone). Fable ma
   rozważyć czy ffmpeg da się użyć z biblioteki Python czy lepiej .exe. (badanie 07 mówi:
   PyAV pokrywa audio, ale render mp4/burn wymaga .exe — ale user chce żeby Fable to sam rozważył).
2. **To samo pytanie dla INNYCH narzędzi** — mkvtoolnix, balcon itd. — biblioteka vs .exe,
   Fable ma zadać sobie to pytanie per narzędzie.

## akcja na jutro
- Napisać POPRAWIONY prompt do Fabla:
  - CAŁKIEM NOWE repo (nowa nazwa) LUB obecne (3 gwiazdki) — user zdecyduje
  - RECYKLING serwisów MangaShift w 100% (nie własna architektura)
  - struktura MangaShift: external/bin, workspace (NIE working_space)
  - NIE kopiować błędów/przekonań z obecnego repo mm_avh
  - Fable ma się zreflektować nad ffmpeg biblioteka vs exe + inne narzędzia
- User idzie spać, wraca jutro.

## DECYZJE (2026-07-12, rano — dzień 2)
- **Repo:** obecne (3 gwiazdki żyją), przebudowa od zera na nowym branchu, nowa nazwa pakietu w środku.
- **Nazwa projektu/pakietu: `AniShift`** (pakiet: `anishift`). Ani (anime) + Shift — siostra MangaShift,
  ta sama rodzina nazw/brand. Zastępuje mm_avh / mm_avh_working_space.

## status
- Plan Sola: docs/brainstorms/2026-07-12-przebudowa-od-zera-PLAN.md (ODRZUCONY)
- Plan Fabla: docs/brainstorms/2026-07-12-przebudowa-od-zera-PLAN-fable.md (ODRZUCONY)
- Materiały (audyt 00-09, spec, wzorce MangaShift) — nadal dobre, zostają.
- Następny krok: poprawiony prompt do Fabla (runda 3) — projekt AniShift.
