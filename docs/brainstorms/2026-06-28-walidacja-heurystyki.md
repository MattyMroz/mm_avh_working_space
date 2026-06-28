# 🔬 Walidacja heurystyki vs Ground Truth (czytanie treści)

> Ground truth: 19 subagentów Sonnet przeczytało TREŚĆ 182 plików ASS i sklasyfikowało style. Heurystyka: czyste metryki (pos/draw/karaoke/punct/linie). Porównanie poniżej.

## 📊 Wynik: **969/979 = 99.0%** zgodności (+ 35 niepewnych heurystyki)

- 🔴 **Cichy lektor** (prawda=DIALOG, heur=ZNAK → pominie mowę): **2**
- 🟡 **Fałszywy dialog** (prawda=ZNAK/PIOSENKA, heur=DIALOG → czyta znak): **8**
- ❓ **Niepewne** (heur się waha): **35**

Legenda werdyktów: 🗣️=DIALOG(czytaj) 🔇=ZNAK(pomiń) ❓=NIEPEWNE. Kolumny: styl | linie | pos% | HEUR | PRAWDA | zgodność.

---

## 🔴 CICHY LEKTOR — heurystyka pominie dialog (sprawdź!)

- **141___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_04__10** | styl `Znaki` (48 linii) — heur=ZNAK ale PRAWDA=DIALOG
- **140___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_03__10** | styl `Znaki` (23 linii) — heur=ZNAK ale PRAWDA=DIALOG

## 🟡 FAŁSZYWY DIALOG — heurystyka czyta znak/piosenkę

- **159___SubsPlease__Yomi_no_Tsugai_-_02__1080p__** | styl `italics` (36 linii) — heur=DIALOG ale PRAWDA=PIOSENKA
- **009___SubsPlease__Toujima_Tanzaburou_wa_Kamen_** | styl `TopCenter` (24 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **193___SubsPlease__Kill_Ao_-_09__1080p___281C95** | styl `On Top` (14 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **025___SubsPlease__Toujima_Tanzaburou_wa_Kamen_** | styl `TopCenter` (9 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **196___SubsPlease__Kill_Ao_-_12__1080p___9C22A8** | styl `On Top` (9 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **037___Erai-raws__Arifureta_Shokugyou_de_Sekai_** | styl `On Top` (4 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **003___Erai-raws__Shiguang_Dailiren_Season_2_-_** | styl `On Top` (2 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **190___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_10** | styl `Q7` (1 linii) — heur=DIALOG ale PRAWDA=ZNAK

---

## 📋 Pełny przegląd per plik

**000___Erai-raws__Shiguang_Dailiren_Season_2_-_01__1080p__Multiple_Subt**
  🗣️ `Default                 ` n= 378 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**001___Erai-raws__Shiguang_Dailiren_Season_2_-_02__1080p__Multiple_Subt**
  🗣️ `Default                 ` n= 335 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**002___Erai-raws__Shiguang_Dailiren_Season_2_-_03__1080p__Multiple_Subt**
  🗣️ `Default                 ` n= 336 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**003___Erai-raws__Shiguang_Dailiren_Season_2_-_04__1080p__Multiple_Subt**
  🗣️ `Default                 ` n= 412 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `On Top                  ` n=   2 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ

**004___Erai-raws__Shiguang_Dailiren_Season_2_-_05__1080p__Multiple_Subt**
  🗣️ `Default                 ` n= 362 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**005___Erai-raws__Shiguang_Dailiren_Season_2_-_06__1080p__Multiple_Subt**
  🗣️ `Default                 ` n= 393 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Overlap                 ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**006___shisha__Genjitsu_no_Yohane_-_Sunshine_in_the_Mirror_-_01__1080p_**
  🗣️ `Yohane                  ` n= 288 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Yohane - Myśli          ` n=  24 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  20 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**007___shisha__Genjitsu_no_Yohane_-_Sunshine_in_the_Mirror_-_02__1080p_**
  🗣️ `Yohane                  ` n= 327 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  14 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Yohane - Myśli          ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**008___shisha__Masamune-kun_no_Revenge_S2_-_01__1080p_AAC_.mkv.ass**
  🗣️ `Masamune                ` n= 300 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Masamune - Myśli        ` n=  46 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  17 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Masamune - Alter        ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**009___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_08__1**
  🗣️ `BottomCenter            ` n= 258 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `TopCenter               ` n=  24 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ

**010___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_09__1**
  🗣️ `Default                 ` n= 192 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  29 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   8 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Top                     ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics Top             ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**011___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_10__1**
  🗣️ `Default                 ` n= 142 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  43 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  11 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**012___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_11__1**
  🗣️ `Default                 ` n= 161 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  24 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  16 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics Top             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**013___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_12__1**
  🗣️ `Default                 ` n= 215 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Top                     ` n=  15 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  14 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**014___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_13__1**
  🗣️ `Default                 ` n= 227 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  46 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  11 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**015___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_14__1**
  🗣️ `Default                 ` n= 186 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italic                  ` n=  13 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Signs                   ` n=  10 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🗣️ `Flashback               ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Top                     ` n=   1 pos=  0 | heur=NIEPEWNE prawda=DIALOG    ❓

**016___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_15__1**
  🗣️ `Default                 ` n= 137 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  81 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italic                  ` n=  49 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   9 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback Italics       ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Top                     ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**017___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_16__1**
  🗣️ `Default                 ` n= 205 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  12 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**018___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_17__1**
  🗣️ `Default                 ` n= 155 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  30 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  18 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  11 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**019___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_18__1**
  🗣️ `Default                 ` n= 229 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  12 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Signs                   ` n=   9 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🗣️ `Flashback               ` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**020___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_19__1**
  🗣️ `Default                 ` n= 283 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  11 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Top                     ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**021___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_20__1**
  🗣️ `BottomCenter            ` n= 269 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `TopCenter               ` n=   9 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**022___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_21__1**
  🗣️ `Default                 ` n= 151 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  85 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italic                  ` n=  17 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  10 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback Italics       ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**023___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_22__1**
  🗣️ `Default                 ` n= 237 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   9 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Top                     ` n=   1 pos=  0 | heur=NIEPEWNE prawda=DIALOG    ❓

**024___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_23__1**
  🗣️ `Default                 ` n= 170 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   7 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**025___SubsPlease__Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai_-_24__1**
  🗣️ `BottomCenter            ` n= 183 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `TopCenter               ` n=   9 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ

**026___SubsPlease__Vigilante_-_Boku_no_Hero_Academia_Illegals_S2_-_07__**
  🗣️ `flashback               ` n= 288 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback italics       ` n=  12 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `main                    ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_Verdana            ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_TimesNewRoman      ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `italics                 ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashbacktop            ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `overlap                 ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**027___SubsPlease__Vigilante_-_Boku_no_Hero_Academia_Illegals_S2_-_08__**
  🗣️ `flashback               ` n= 214 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `main                    ` n=  67 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback italics       ` n=  24 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_Verdana            ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_TimesNewRoman      ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_TrebuchetMS        ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_Arial              ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**028___SubsPlease__Vigilante_-_Boku_no_Hero_Academia_Illegals_S2_-_09__**
  🗣️ `main                    ` n= 340 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `top                     ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_Verdana            ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_TimesNewRoman      ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_Arial              ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_TrebuchetMS        ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**029___SubsPlease__Yuusha_no_Kuzu_-_02__1080p___21A8CA53_.mkv.ass**
  🗣️ `Default                 ` n= 153 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n= 119 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_generic            ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `flashback               ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `top                     ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**030___shisha__Jigokuraku_2nd_Season_-_09.mkv.ass**
  🗣️ `Jigokuraku              ` n= 225 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Jigokuraku - Myśli      ` n=  50 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Kasukana Hana           ` n=  25 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Jigokuraku - Alt        ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**031___lycoris.cafe__Busamen_Gachi_Fighter_-_5__1080p_.mkv.ass**
  🗣️ `Default                 ` n= 253 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  74 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `default - top           ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `eptitle                 ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default top             ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —
  🗣️ `flashback italics       ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `handwriting             ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**032___lycoris.cafe__Busamen_Gachi_Fighter_-_06__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 273 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  74 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `trebuchet-black-grey box` n=   7 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default - top           ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `eptitle                 ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default top             ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `arial                   ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**036___Erai-raws__Arifureta_Shokugyou_de_Sekai_Saikyou_3rd_Season_-_09_**
  🗣️ `Default                 ` n= 294 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `On Top                  ` n=   2 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**037___Erai-raws__Arifureta_Shokugyou_de_Sekai_Saikyou_3rd_Season_-_10_**
  🗣️ `Default                 ` n= 266 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `On Top                  ` n=   4 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ

**038___SubsPlease__One_Room__Hiatari_Futsuu__Tenshi-tsuki_-_01__1080p__**
  🗣️ `Default                 ` n= 305 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  70 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_generic            ` n=  28 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `top                     ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italicstop              ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**039___SubsPlease__Tsue_to_Tsurugi_no_Wistoria_-_02__1080p___53E76DBF_.**
  🗣️ `Default                 ` n= 225 pos=  8 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Italics          ` n=  39 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  21 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=  15 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback - Top         ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top + Italics    ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**040___SubsPlease__Tsue_to_Tsurugi_no_Wistoria_-_03__1080p___6D17C648_.**
  🗣️ `Main                    ` n= 186 pos= 12 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Italics          ` n=  54 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  21 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=  12 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback - Italics     ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**041___SubsPlease__Bartender_-_Kami_no_Glass_-_01__1080p___AB352C1E_.mk**
  🗣️ `Default                 ` n= 302 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  47 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=  22 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultTop              ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**042___SubsPlease__Bartender_-_Kami_no_Glass_-_02__1080p___26052902_.mk**
  🗣️ `Default                 ` n= 315 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  21 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_generic            ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `flashback               ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**043___SubsPlease__Bartender_-_Kami_no_Glass_-_03__1080p___263098CD_.mk**
  🗣️ `Default                 ` n= 305 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  21 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  20 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_generic            ` n=   3 pos= 67 | heur=ZNAK     prawda=ZNAK      ✅

**044___SubsPlease__Bartender_-_Kami_no_Glass_-_04__1080p___203FDCCB_.mk**
  🗣️ `Default                 ` n= 304 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  15 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultItalics          ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_generic            ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**045___SubsPlease__Bartender_-_Kami_no_Glass_-_05__1080p___CCA86BE8_.mk**
  🗣️ `Default                 ` n= 228 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  75 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  28 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_generic            ` n=  13 pos= 85 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**046___SubsPlease__Bartender_-_Kami_no_Glass_-_06__1080p___29104EC1_.mk**
  🗣️ `Default                 ` n= 299 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_generic            ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**047___SubsPlease__Bartender_-_Kami_no_Glass_-_07__1080p___EF05B5B1_.mk**
  🗣️ `Default                 ` n= 294 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  14 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_generic            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**048___SubsPlease__Bartender_-_Kami_no_Glass_-_08__1080p___6DCDA080_.mk**
  🗣️ `Default                 ` n= 191 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  67 pos= 94 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=  43 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_generic            ` n=  18 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultTop              ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `FlashbackItalics        ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**049___SubsPlease__Bartender_-_Kami_no_Glass_-_09__1080p___90221C7B_.mk**
  🗣️ `Default                 ` n= 276 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  13 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_generic            ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultTop              ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —

**050___SubsPlease__Bartender_-_Kami_no_Glass_-_10__1080p___9ADB96A4_.mk**
  🗣️ `Default                 ` n= 251 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  23 pos= 91 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=  21 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  14 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**051___SubsPlease__Bartender_-_Kami_no_Glass_-_11__1080p___83B90909_.mk**
  🗣️ `Default                 ` n= 230 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  53 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  36 pos= 89 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultItalics          ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**052___SubsPlease__Bartender_-_Kami_no_Glass_-_12__1080p___F5327758_.mk**
  🗣️ `Default                 ` n= 262 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultItalics          ` n=  19 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  12 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**071___SubsPlease__Kumichou_Musume_to_Sewagakari_-_04__1080p___C5C682F5**
  🗣️ `Default                 ` n= 220 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  69 pos= 71 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=  62 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bottom_Text             ` n=  26 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - Top           ` n=  20 pos=  5 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Handwritten_Borderless  ` n=  10 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**072___SubsPlease__Kumichou_Musume_to_Sewagakari_-_05__1080p___FF8F000F**
  🗣️ `Default                 ` n= 307 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  40 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  37 pos= 95 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - Top           ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Character_Profile       ` n=   2 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Handwritten_Borderless  ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**073___SubsPlease__Kumichou_Musume_to_Sewagakari_-_06__1080p___714C07B8**
  🗣️ `Default                 ` n= 376 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  13 pos= 92 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default - Top           ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Handwritten_Borderless  ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**074___SubsPlease__Kumichou_Musume_to_Sewagakari_-_07__1080p___CEBAED9F**
  🗣️ `Default                 ` n= 199 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  71 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  35 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  12 pos= 67 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback_Italics       ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default - Top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Handwritten_Borderless  ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**075___SubsPlease__Kumichou_Musume_to_Sewagakari_-_08__1080p___7117C442**
  🗣️ `Default                 ` n= 178 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n= 175 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  15 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  10 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback_Italics       ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Character_Profile       ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Handwritten_Borderless  ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - Top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**076___SubsPlease__Kumichou_Musume_to_Sewagakari_-_09__1080p___1E97A8FC**
  🗣️ `Default                 ` n= 227 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n= 129 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  36 pos= 94 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback_Italics       ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default - Top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**077___SubsPlease__Kumichou_Musume_to_Sewagakari_-_10__1080p___1E97A8FC**
  🗣️ `Default                 ` n= 295 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - Top           ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**078___SubsPlease__Kumichou_Musume_to_Sewagakari_-_11__1080p___AB4856C7**
  🗣️ `Default                 ` n= 262 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  11 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=  10 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default - Top           ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Handwritten_Borderless  ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Character_Profile       ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `End_Title               ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**079___SubsPlease__Kumichou_Musume_to_Sewagakari_-_12__1080p___E52FA423**
  🗣️ `Default                 ` n= 259 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  75 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  11 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback_Italics       ` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Bordered_TopSign        ` n=   7 pos= 57 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - Top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Handwritten_Borderless  ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Mid_Title               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**080__R14.mkv.ass**
  🗣️ `Re: Zero III            ` n= 128 pos=  2 | heur=DIALOG   prawda=?         —
  🗣️ `Re: Zero III - Retrospek` n=  98 pos=  1 | heur=DIALOG   prawda=?         —
  🗣️ `Re: Zero III - Myśli    ` n=  40 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `NOX LUX by MYTH & ROID  ` n=  18 pos= 56 | heur=ZNAK     prawda=?         —
  🗣️ `Re: Zero III - Retrospek` n=   3 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `Znaki                   ` n=   2 pos=100 | heur=ZNAK     prawda=?         —
  🗣️ `Re: Zero III - Alter    ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —

**081__R15.mkv.ass**
  🗣️ `Re: Zero III            ` n= 324 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Reweave by Konomi Suzuki` n=  19 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Reweave by Konomi Suzuki` n=  19 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Re: Zero III - Retrospek` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Re: Zero III - Alter    ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Re: Zero III - Myśli    ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**082__10.mkv.ass**
  🗣️ `Default                 ` n= 263 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**083__11.mkv.ass**
  🗣️ `Default                 ` n= 360 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**085__7.mkv.ass**
  🗣️ `Default                 ` n= 305 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**086__8.mkv.ass**
  🗣️ `Default                 ` n= 293 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**087__9.mkv.ass**
  🗣️ `Default                 ` n= 282 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**088__Seikon_no_Qwaser_S01E01.mkv.ass**
  🗣️ `Default                 ` n= 301 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Note                    ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**089__Seikon_no_Qwaser_S01E02.mkv.ass**
  🗣️ `Default                 ` n= 303 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**090__Seikon_no_Qwaser_S01E03.mkv.ass**
  🗣️ `Default                 ` n= 287 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**091__Seikon_no_Qwaser_S01E04.mkv.ass**
  🗣️ `Default                 ` n= 296 pos=  4 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**092__Seikon_no_Qwaser_S01E05.mkv.ass**
  🗣️ `Default                 ` n= 292 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Note                    ` n=   2 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**093__Seikon_no_Qwaser_S01E06.mkv.ass**
  🗣️ `Default                 ` n= 338 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   6 pos= 67 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Note                    ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**094__Seikon_no_Qwaser_S01E07.mkv.ass**
  🗣️ `Default                 ` n= 298 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   4 pos= 75 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Note                    ` n=   2 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**095__Seikon_no_Qwaser_S01E08.mkv.ass**
  🗣️ `Default                 ` n= 296 pos=  4 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —

**096__Seikon_no_Qwaser_S01E09.mkv.ass**
  🗣️ `Default                 ` n= 310 pos=  4 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**097__Seikon_no_Qwaser_S01E10.5_OVA.mkv.ass**
  🗣️ `Default                 ` n= 301 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default-alt             ` n=  16 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `ED Romaji               ` n=  14 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `OP Romaji               ` n=  14 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `OP Kanji                ` n=  13 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `OP English              ` n=  13 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `ED Kanji                ` n=  12 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `ED English              ` n=  12 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Signs                   ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Note                    ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Signs2                  ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**098__Seikon_no_Qwaser_S01E10.mkv.ass**
  🗣️ `Default                 ` n= 265 pos=  4 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Note                    ` n=   3 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**099__Seikon_no_Qwaser_S01E11.mkv.ass**
  🗣️ `Default                 ` n= 296 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `BloodSign               ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**100__Seikon_no_Qwaser_S01E12.mkv.ass**
  🗣️ `Default                 ` n= 315 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**101__Seikon_no_Qwaser_S01E13.mkv.ass**
  🗣️ `Default                 ` n= 327 pos=  3 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**102__Seikon_no_Qwaser_S01E14.mkv.ass**
  🗣️ `Default                 ` n= 278 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  12 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**103__Seikon_no_Qwaser_S01E15.mkv.ass**
  🗣️ `Default                 ` n= 215 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**104__Seikon_no_Qwaser_S01E16.mkv.ass**
  🗣️ `Default                 ` n= 288 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**105__Seikon_no_Qwaser_S01E17.mkv.ass**
  🗣️ `Default                 ` n= 246 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**106__Seikon_no_Qwaser_S01E18.mkv.ass**
  🗣️ `Default                 ` n= 314 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default-alt             ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**107__Seikon_no_Qwaser_S01E19.mkv.ass**
  🗣️ `Default                 ` n= 266 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**108__Seikon_no_Qwaser_S01E20.mkv.ass**
  🗣️ `Default                 ` n= 271 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**109__Seikon_no_Qwaser_S01E21.mkv.ass**
  🗣️ `Default                 ` n= 273 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default-alt             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**110__Seikon_no_Qwaser_S01E22.mkv.ass**
  🗣️ `Default                 ` n= 276 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**111__Seikon_no_Qwaser_S01E23.mkv.ass**
  🗣️ `Default                 ` n= 295 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**112__Seikon_no_Qwaser_S01E24.mkv.ass**
  🗣️ `Default                 ` n= 267 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `OP Romaji               ` n=  26 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `OP English              ` n=  25 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `OP Kanji                ` n=  23 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Signs                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**113__Seikon_no_Qwaser_S02E01.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 285 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  20 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji OP                ` n=  19 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji ED                ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Seikon no Qwaser II sign` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default                 ` n=   3 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `SubDesu Logo            ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**114__Seikon_no_Qwaser_S02E02.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 261 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  20 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji OP                ` n=  19 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji ED                ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Default                 ` n=   4 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `SubDesu Logo            ` n=   2 pos=100 | heur=ZNAK     prawda=?         —
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**115__Seikon_no_Qwaser_S02E03.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 265 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  20 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji OP                ` n=  19 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji ED                ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Default                 ` n=   3 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `Seikon no Qwaser II sign` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `SubDesu Logo            ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**116__Seikon_no_Qwaser_S02E04.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 298 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  20 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji OP                ` n=  19 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji ED                ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default                 ` n=   2 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**117__Seikon_no_Qwaser_S02E05.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 286 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  20 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji OP                ` n=  19 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji ED                ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default                 ` n=   2 pos=  0 | heur=DIALOG   prawda=?         —
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**118__Seikon_no_Qwaser_S02E06.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 302 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  20 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji OP                ` n=  19 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Kanji ED                ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  15 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default                 ` n=   1 pos=  0 | heur=DIALOG   prawda=?         —

**119__Seikon_no_Qwaser_S02E07.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 266 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**120__Seikon_no_Qwaser_S02E08.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 354 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Default                 ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**121__Seikon_no_Qwaser_S02E09.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 315 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Default                 ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**122__Seikon_no_Qwaser_S02E10.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 339 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Seikon no Qwaser II sign` n=  25 pos= 92 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Romanji OP              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Seikon no Qwaser II sign` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `SubDesu Logo            ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**123__Seikon_no_Qwaser_S02E11.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 354 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Seikon no Qwaser II sign` n=  11 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**124__Seikon_no_Qwaser_S02E12.mkv.ass**
  🗣️ `Seikon no Qwaser II Dial` n= 331 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Romanji OP              ` n=  14 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English OP              ` n=  13 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Romanji ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `English ED              ` n=  12 pos=  0 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `SubDesu Logo            ` n=   5 pos= 80 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Seikon no Qwaser II sign` n=   1 pos=  0 | heur=ZNAK     prawda=?         —

**125___lycoris.cafe__NUKITASHI_THE_ANIMATION_-_08__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 338 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Text                    ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default - top           ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**126___lycoris.cafe__NUKITASHI_THE_ANIMATION_-_09__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 336 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Text                    ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default - top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**127___lycoris.cafe__NUKITASHI_THE_ANIMATION_-_10__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 345 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `default - top           ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Text                    ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**128___lycoris.cafe__NUKITASHI_THE_ANIMATION_-_11__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 335 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default - top           ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**129___Erai-raws__Sanda_-_01__1080p_AMZN_WEBRip_HEVC_EAC3__MultiSub__7E**
  🗣️ `Default                 ` n= 455 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**130___Erai-raws__Sanda_-_02__1080p_AMZN_WEBRip_HEVC_EAC3__MultiSub__9B**
  🗣️ `Default                 ` n= 457 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**131___Erai-raws__Sanda_-_03__1080p_AMZN_WEB-DL_AVC_EAC3__MultiSub__31A**
  🗣️ `Default                 ` n= 416 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**132___Erai-raws__Sanda_-_04__1080p_AMZN_WEB-DL_AVC_EAC3__MultiSub__C6C**
  🗣️ `Default                 ` n= 385 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**133___Erai-raws__Sanda_-_05__1080p_AMZN_WEB-DL_AVC_EAC3__MultiSub__B2A**
  🗣️ `Default                 ` n= 429 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**134___Erai-raws__Sanda_-_06__1080p_AMZN_WEB-DL_AVC_EAC3__MultiSub__6F8**
  🗣️ `Default                 ` n= 416 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**135___Erai-raws__Sanda_-_07__1080p_AMZN_WEB-DL_AVC_EAC3__MultiSub__8AA**
  🗣️ `Default                 ` n= 435 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**136___shisha__Haite_Kudasai_Takamine-san_-_02.mkv.ass**
  🗣️ `Takamine                ` n= 185 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Takamine - Myśli        ` n=  93 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  28 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Masami Okui - Baby Baby ` n=  20 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🔇 `Eyecatch                ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Takamine - Alt          ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_11988_145_Please_Pu` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_6229_38_Student_Cou` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Episode Title           ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**137___lycoris.cafe__Class_de_2-banme_ni_Kawaii_Onnanoko_to_Tomodachi_n**
  🗣️ `Default                 ` n= 284 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultItalics          ` n=  42 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=  14 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Czat                    ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**138___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_01__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 277 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  60 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  21 pos= 95 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `TS                      ` n=  15 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Góra              ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**139___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_02__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 247 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  77 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Furry Góra              ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=   9 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**140___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_03__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 251 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  51 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=  23 pos=100 | heur=ZNAK     prawda=DIALOG    🔴CICHY
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Furry Góra              ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**141___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_04__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 264 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  48 pos= 98 | heur=ZNAK     prawda=DIALOG    🔴CICHY
  🗣️ `Furry Kursywa           ` n=  45 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  38 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Furry Góra              ` n=  17 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**142___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_05__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 304 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  73 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  37 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Furry Góra              ` n=  14 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  11 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**143___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_06__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 236 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  59 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  37 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=  13 pos= 92 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Góra              ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**144___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_07__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 238 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  57 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  37 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**145___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_08__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 261 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  64 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Kursywa           ` n=  44 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=   6 pos= 83 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Góra              ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**146___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_09__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 334 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  41 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Furry Góra              ` n=  12 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `TS                      ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**147___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_10__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 306 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  42 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  37 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=   8 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Góra              ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**148___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_11__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 301 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `TS                      ` n=  64 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Kursywa           ` n=  35 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=  19 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Furry Góra              ` n=   4 pos=  0 | heur=NIEPEWNE prawda=DIALOG    ❓
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**149___Fuji__Kimi_to_Koete_Koi_ni_Naru_-_12__1080p_.mkv.ass**
  🗣️ `Furry                   ` n= 269 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Furry Kursywa           ` n=  46 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Opening                 ` n=  30 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Ending                  ` n=  20 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `Znaki                   ` n=   8 pos= 88 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `TS                      ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Furry Góra              ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Kredki                  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**150___SubsPlease__Kami_no_Niwatsuki_Kusunoki-tei_-_01__720p___F6575706**
  🗣️ `Default                 ` n= 343 pos=  7 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  26 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default Top             ` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**151___SubsPlease__Kami_no_Niwatsuki_Kusunoki-tei_-_02__1080p___59C6C03**
  🗣️ `Default                 ` n= 356 pos=  5 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  11 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Default Top             ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**152___SubsPlease__Mata_Korosarete_Shimatta_no_desu_ne__Tantei-sama_-_0**
  🗣️ `Default                 ` n= 271 pos= 14 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  43 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Top                     ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**153___SubsPlease__Mata_Korosarete_Shimatta_no_desu_ne__Tantei-sama_-_0**
  🗣️ `Default                 ` n= 264 pos= 11 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  37 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Top                     ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**154___SubsPlease__Shibou_Yuugi_de_Meshi_wo_Kuu._-_07__1080p___144627FF**
  🗣️ `main                    ` n= 114 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=  22 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  20 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback italics       ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `top                     ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**155___SubsPlease__Shibou_Yuugi_de_Meshi_wo_Kuu._-_08__1080p___93FFCD30**
  🗣️ `main                    ` n= 178 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  17 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `top                     ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_Georgia            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**156___SubsPlease__Shibou_Yuugi_de_Meshi_wo_Kuu._-_09__1080p___DE87BF78**
  🗣️ `main                    ` n= 163 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italicstop              ` n=  12 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `top                     ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**157___SubsPlease__Shibou_Yuugi_de_Meshi_wo_Kuu._-_10__1080p___6CB8E615**
  🗣️ `italics                 ` n=  70 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=  61 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback italics       ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `main                    ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashbackitalicstop     ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**158___SubsPlease__Shibou_Yuugi_de_Meshi_wo_Kuu._-_11__1080p___F8ECA54A**
  🗣️ `flashback               ` n=  77 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `main                    ` n=  72 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  26 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashbacktop            ` n=  16 pos=  0 | heur=DIALOG   prawda=?         —

**159___SubsPlease__Yomi_no_Tsugai_-_02__1080p___81EC5E72_.mkv.ass**
  🗣️ `Default                 ` n= 303 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  36 pos=  0 | heur=DIALOG   prawda=PIOSENKA  🟡FALSZ
  🔇 `sign_generic            ` n=  14 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `flashback               ` n=  11 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**160___lycoris.cafe__Mata_Korosarete_Shimatta_no_desu_ne_Tantei-sama_-_**
  🗣️ `Default                 ` n= 294 pos=  9 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics top             ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `top                     ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**161___shisha__Tsue_to_Tsurugi_no_Wistoria_Season_2_-_01.mkv.ass**
  🗣️ `Wistoria                ` n= 295 pos=  1 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=  63 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Wistoria - Myśli        ` n=  44 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Wistoria - Alter        ` n=  12 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**162__Gals_Can_t_Be_Kind_to_Otaku_S01E11_VOSTFR_1080p_WEB_x264_AAC_-Tsu**
  🗣️ `Default                 ` n= 284 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italique                ` n=  44 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign                    ` n=  24 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `TiretsDefault           ` n=  16 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**163__Gals_Can_t_Be_Kind_to_Otaku_S01E12_VOSTFR_1080p_WEB_x264_AAC_-Tsu**
  🗣️ `Default                 ` n= 222 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italique                ` n=  98 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Sign                    ` n=  15 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🗣️ `TiretsDefault           ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**164___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_01__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 294 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_34006_297_Circuit_B` n=  11 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Sign_Basic              ` n=   8 pos= 88 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text_Box       ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_12329_149_Solid    ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**165___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_02__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 285 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_4811_65_Electricity` n=   9 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Sign_Basic              ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text_Box       ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback_Italics       ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**166___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_03__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 200 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  47 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=  16 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Acquired_Text_Box       ` n=   9 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_4811_65_Electricity` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback_Italics       ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**167___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_04__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 215 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  21 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_27936_262_Ethanol  ` n=  21 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=  19 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Sign_Basic              ` n=   3 pos= 33 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Acquired_Text_Box       ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**168___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_05__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 266 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  16 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   6 pos= 67 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text_Box       ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**169___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_06__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 245 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_27936_262_Ethanol  ` n=   9 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Acquired_Text_Box       ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Flashback               ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_17052_152_Phosphate` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**170___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_07__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 233 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Acquired_Text_Box       ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**171___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_08__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 252 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_27936_262_Ethanol  ` n=  14 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Sign_Basic              ` n=  10 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text_Box       ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**172___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_09__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 245 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  16 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text_Box       ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_27936_262_Ethanol  ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**173___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_10__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 306 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  25 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_27936_262_Ethanol  ` n=  11 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text_Box       ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Acquired_Text           ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**174___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_11__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 239 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  18 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   8 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Time Setting            ` n=   1 pos=100 | heur=ZNAK     prawda=?         —
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**175___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_12__1080p_CR_WEBRi**
  🗣️ `Main                    ` n= 232 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  15 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Episode            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Next_Ep_Title           ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**176___Erai-raws__Dr_Stone_-_Science_Future_Part_3_-_13__1080p_CR_WEB-D**
  🗣️ `Main                    ` n= 221 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `sign_8958_97_Ramen      ` n=  28 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Italics                 ` n=  15 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   5 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Ep_Title                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**177___Erai-raws__Koori_no_Jouheki_-_09__1080p_NF_WEB-DL_AVC_AAC__Multi**
  🗣️ `Default                 ` n= 374 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**178___Erai-raws__Koori_no_Jouheki_-_10__1080p_NF_WEB-DL_AVC_AAC__Multi**
  🗣️ `Default                 ` n= 470 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**179___Erai-raws__Koori_no_Jouheki_-_11__1080p_NF_WEB-DL_AVC_AAC__Multi**
  🗣️ `Default                 ` n= 422 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**180___Erai-raws__Koori_no_Jouheki_-_12__1080p_NF_WEB-DL_AVC_AAC__Multi**
  🗣️ `Default                 ` n= 379 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**181___Erai-raws__Koori_no_Jouheki_-_13__1080p_NF_WEB-DL_AVC_AAC__Multi**
  🗣️ `Default                 ` n= 404 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**182___SubsPlease__Class_de_2-banme_ni_Kawaii_Onnanoko_to_Tomodachi_ni_**
  🗣️ `Default                 ` n= 294 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `DefaultItalics          ` n=  33 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Signs                   ` n=   5 pos= 40 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `DefaultTop              ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `FlashbackTop            ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**183___SubsPlease__Himekishi_wa_Barbaroi_no_Yome_-_11__1080p___AB8767F9**
  🗣️ `Main                    ` n= 283 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=  21 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics - Top           ` n=   2 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Time/Setting            ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**184___SubsPlease__Himekishi_wa_Barbaroi_no_Yome_-_12__1080p___CB5DD8F1**
  🗣️ `Main                    ` n= 251 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  31 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Main - Top              ` n=  22 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Time/Setting            ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Sign_Basic              ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**185___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_05__1080p___6706CE18_.mkv.**
  🗣️ `Q1                      ` n= 389 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q0                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🗣️ `Q4                      ` n=  19 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q2                      ` n=  19 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q3                      ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q5                      ` n=   3 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q6                      ` n=   2 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  ❓ `Q7                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**186___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_06__1080p___7DF701F0_.mkv.**
  🗣️ `Q1                      ` n= 403 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q0                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🔇 `Q2                      ` n=  18 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Q3                      ` n=  16 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q4                      ` n=  12 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q7                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q6                      ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q5                      ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**187___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_07__1080p___8322CCD7_.mkv.**
  🗣️ `Q1                      ` n= 359 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q0                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🗣️ `Q3                      ` n=  10 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q7                      ` n=   9 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q2                      ` n=   8 pos= 75 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q4                      ` n=   5 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q6                      ` n=   4 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q8                      ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q10                     ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q5                      ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q9                      ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**188___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_08__1080p___02B5FDFE_.mkv.**
  🗣️ `Q0                      ` n= 369 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q1                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🗣️ `Q2                      ` n=   9 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q3                      ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q4                      ` n=   2 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q5                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**189___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_09__1080p___E2C845C1_.mkv.**
  🗣️ `Q0                      ` n= 398 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q1                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🗣️ `Q2                      ` n=  16 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q7                      ` n=   3 pos= 67 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q4                      ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q5                      ` n=   2 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  ❓ `Q8                      ` n=   2 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q10                     ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q3                      ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q6                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q11                     ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q9                      ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**190___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_10__1080p___EAF81DE3_.mkv.**
  🗣️ `Q1                      ` n= 414 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q0                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🔇 `Q5                      ` n=   9 pos= 89 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q3                      ` n=   8 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Q2                      ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q4                      ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Q7                      ` n=   1 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ
  ❓ `Q8                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q6                      ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**191___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_11__1080p___288E8C79_.mkv.**
  🗣️ `Q1                      ` n= 426 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q0                      ` n=  44 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🔇 `Q2                      ` n=  16 pos= 56 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Q3                      ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q4                      ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q6                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q5                      ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅

**192___SubsPlease__Isekai_Nonbiri_Nouka_S2_-_12__1080p___12C3D6B8_.mkv.**
  🗣️ `Q1                      ` n= 466 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `Q10                     ` n=  33 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  ❓ `Q0                      ` n=  20 pos=  0 | heur=NIEPEWNE prawda=PIOSENKA  ❓
  🗣️ `Q3                      ` n=  19 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Q5                      ` n=   7 pos= 71 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q2                      ` n=   2 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q4                      ` n=   2 pos= 50 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `Q6                      ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🔇 `Q7                      ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q8                      ` n=   1 pos=  0 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Q9                      ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**193___SubsPlease__Kill_Ao_-_09__1080p___281C95F2_.mkv.ass**
  🗣️ `Default                 ` n= 363 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `On Top                  ` n=  14 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ
  🗣️ `Italics                 ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**194___SubsPlease__Kill_Ao_-_10__1080p___5C9E744A_.mkv.ass**
  🗣️ `Default                 ` n= 371 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `On Top                  ` n=  16 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓
  🗣️ `Italics                 ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**195___SubsPlease__Kill_Ao_-_11__1080p___CBC70D81_.mkv.ass**
  🗣️ `Default                 ` n= 421 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `On Top                  ` n=  17 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**196___SubsPlease__Kill_Ao_-_12__1080p___9C22A8A0_.mkv.ass**
  🗣️ `Default                 ` n= 422 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `On Top                  ` n=   9 pos=  0 | heur=DIALOG   prawda=ZNAK      🟡FALSZ
  🗣️ `Italics                 ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**197___SubsPlease__Ponkotsu_Fuuki_Iin_to_Skirt-take_ga_Futekisetsu_na_J**
  🗣️ `Main                    ` n= 338 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n= 103 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=  48 pos= 85 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=  17 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback               ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics - Top           ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Flashback - Top         ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Narration               ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**198___SubsPlease__Ponkotsu_Fuuki_Iin_to_Skirt-take_ga_Futekisetsu_na_J**
  🗣️ `Main                    ` n= 369 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics                 ` n=  32 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=  27 pos= 93 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Main - Top              ` n=  13 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Narration               ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Italics - Top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅

**199___lycoris.cafe__Honzuki_no_Gekokujou-_Ryoushu_no_Youjo_-_9__1080p_**
  🗣️ `Default                 ` n= 275 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  38 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `ep title                ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - top           ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign                    ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `eyecatch                ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  ❓ `illustration_by_        ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**200___lycoris.cafe__Honzuki_no_Gekokujou_S4_-_07__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 244 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  30 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign                    ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `flashback               ` n=   6 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `ep title                ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Default - top           ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `eyecatch                ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `default_top             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics_top             ` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  ❓ `illustration_by_        ` n=   1 pos=  0 | heur=NIEPEWNE prawda=ZNAK      ❓

**201___lycoris.cafe__Honzuki_no_Gekokujou_S4_-_08__source-mkv_.mkv.ass**
  🗣️ `Default                 ` n= 239 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `italics                 ` n=  55 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `flashback               ` n=   7 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `ep title                ` n=   4 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `eyecatch                ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `selfplug                ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `title                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sfx                     ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `illustration_by_        ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**202___lycoris.cafe__Tensei_Shitara_Slime_Datta_Ken_4th_Season_-_9__108**
  🗣️ `Tensura - Podstawowe    ` n= 250 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Tensura - Kursywa       ` n=  56 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Tensura - Górne Kursywa ` n=  17 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Tensura - Górne         ` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Creditsy                ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Tytuł Odcinka           ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Znaki/podpisy           ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Tytuł Następnego Odcinka` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Tytuł                   ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**204___FrixySubs__Dr._STONE_-_S04E25__1080p_CR_WEB-DL_H.264_AAC___Napis**
  🔇 `Rysunki                 ` n=6000 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Dr.Stone - Podstawowe   ` n= 282 pos=  4 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Dr. Stone - Okienka     ` n=  22 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Dr. Stone OP2 Tłumaczeni` n=  16 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🔇 `sign_34006_297_Circuit_B` n=  11 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Disclaimer              ` n=   6 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Dr.Stone - Kursywa      ` n=   4 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Sign_Basic              ` n=   3 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `Dr Stone - Zapowiedź    ` n=   2 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🔇 `sign_12329_149_Solid    ` n=   1 pos=100 | heur=ZNAK     prawda=ZNAK      ✅

**205___shisha__Classroom_of_the_Elite_S4_-_16__1080p_.mkv.ass**
  🔇 `MONSTER -  Eir Aoi [PL] ` n= 387 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Classroom of the Elite  ` n= 333 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `MONSTER -  Eir Aoi [PL] ` n=  58 pos=100 | heur=ZNAK     prawda=PIOSENKA  ✅
  🗣️ `Classroom of the Elite -` n=  17 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🔇 `Znaki                   ` n=   7 pos=100 | heur=ZNAK     prawda=ZNAK      ✅
  🗣️ `Classroom of the Elite -` n=   3 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
  🗣️ `Classroom of the Elite -` n=   1 pos=  0 | heur=DIALOG   prawda=DIALOG    ✅
