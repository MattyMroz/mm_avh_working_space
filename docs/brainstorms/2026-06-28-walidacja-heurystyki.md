# 🔬 Walidacja heurystyki vs Ground Truth (czytanie treści)

> Ground truth: 19 subagentów Sonnet przeczytało TREŚĆ 182 plików ASS i sklasyfikowało style. Heurystyka: czyste metryki (pos/draw/karaoke/punct/linie). Porównanie poniżej.

## 📊 Wynik: **969/979 = 99.0%** zgodności (+ 35 niepewnych heurystyki)

- 🔴 **Cichy lektor** (prawda=DIALOG, heur=ZNAK → pominie mowę): **2**
- 🟡 **Fałszywy dialog** (prawda=ZNAK/PIOSENKA, heur=DIALOG → czyta znak): **8**
- ❓ **Niepewne** (heur się waha): **35**

Legenda werdyktów: 🗣️=DIALOG(czytaj) 🔇=ZNAK(pomiń) ❓=NIEPEWNE. Kolumny: styl | linie | pos% | HEUR | PRAWDA | zgodność.

______________________________________________________________________

## 🔴 CICHY LEKTOR — heurystyka pominie dialog (sprawdź!)

- **141\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-\_04\_\_10** | styl `Znaki` (48 linii) — heur=ZNAK ale PRAWDA=DIALOG
- **140\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-\_03\_\_10** | styl `Znaki` (23 linii) — heur=ZNAK ale PRAWDA=DIALOG

## 🟡 FAŁSZYWY DIALOG — heurystyka czyta znak/piosenkę

- **159\_\_\_SubsPlease\_\_Yomi_no_Tsugai\_-_02\_\_1080p_\_** | styl `italics` (36 linii) — heur=DIALOG ale PRAWDA=PIOSENKA
- **009\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen\_** | styl `TopCenter` (24 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **193\_\_\_SubsPlease\_\_Kill_Ao\_-\_09\_\_1080p\_\_\_281C95** | styl `On Top` (14 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **025\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen\_** | styl `TopCenter` (9 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **196\_\_\_SubsPlease\_\_Kill_Ao\_-\_12\_\_1080p\_\_\_9C22A8** | styl `On Top` (9 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **037\_\_\_Erai-raws\_\_Arifureta_Shokugyou_de_Sekai\_** | styl `On Top` (4 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **003\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_** | styl `On Top` (2 linii) — heur=DIALOG ale PRAWDA=ZNAK
- **190\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-\_10** | styl `Q7` (1 linii) — heur=DIALOG ale PRAWDA=ZNAK

______________________________________________________________________

## 📋 Pełny przegląd per plik

**000\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_01\_\_1080p\_\_Multiple_Subt**
🗣️ `Default                 ` n= 378 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**001\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_02\_\_1080p\_\_Multiple_Subt**
🗣️ `Default                 ` n= 335 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**002\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_03\_\_1080p\_\_Multiple_Subt**
🗣️ `Default                 ` n= 336 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**003\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_04\_\_1080p\_\_Multiple_Subt**
🗣️ `Default                 ` n= 412 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `On Top                  ` n= 2 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ

**004\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_05\_\_1080p\_\_Multiple_Subt**
🗣️ `Default                 ` n= 362 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**005\_\_\_Erai-raws\_\_Shiguang_Dailiren_Season_2\_-\_06\_\_1080p\_\_Multiple_Subt**
🗣️ `Default                 ` n= 393 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Overlap                 ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**006\_\_\_shisha\_\_Genjitsu_no_Yohane\_-_Sunshine_in_the_Mirror_-_01\_\_1080p_**
🗣️ `Yohane                  ` n= 288 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Yohane - Myśli          ` n= 24 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 20 pos=100 | heur=ZNAK prawda=ZNAK ✅

**007\_\_\_shisha\_\_Genjitsu_no_Yohane\_-_Sunshine_in_the_Mirror_-_02\_\_1080p_**
🗣️ `Yohane                  ` n= 327 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 14 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Yohane - Myśli          ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**008\_\_\_shisha\_\_Masamune-kun_no_Revenge_S2\_-_01\_\_1080p_AAC_.mkv.ass**
🗣️ `Masamune                ` n= 300 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Masamune - Myśli        ` n= 46 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 17 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Masamune - Alter        ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**009\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_08\_\_1**
🗣️ `BottomCenter            ` n= 258 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `TopCenter               ` n= 24 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ

**010\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_09\_\_1**
🗣️ `Default                 ` n= 192 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 29 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 8 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Top                     ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics Top             ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**011\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_10\_\_1**
🗣️ `Default                 ` n= 142 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 43 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 11 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**012\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_11\_\_1**
🗣️ `Default                 ` n= 161 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 24 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 16 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics Top             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**013\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_12\_\_1**
🗣️ `Default                 ` n= 215 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Top                     ` n= 15 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 14 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**014\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_13\_\_1**
🗣️ `Default                 ` n= 227 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 46 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 11 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**015\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_14\_\_1**
🗣️ `Default                 ` n= 186 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italic                  ` n= 13 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Signs                   ` n= 10 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🗣️ `Flashback               ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Top                     ` n= 1 pos= 0 | heur=NIEPEWNE prawda=DIALOG ❓

**016\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_15\_\_1**
🗣️ `Default                 ` n= 137 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 81 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italic                  ` n= 49 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 9 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback Italics       ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Top                     ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**017\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_16\_\_1**
🗣️ `Default                 ` n= 205 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 12 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**018\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_17\_\_1**
🗣️ `Default                 ` n= 155 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 30 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 18 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 11 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**019\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_18\_\_1**
🗣️ `Default                 ` n= 229 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 12 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Signs                   ` n= 9 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🗣️ `Flashback               ` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**020\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_19\_\_1**
🗣️ `Default                 ` n= 283 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 11 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Top                     ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**021\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_20\_\_1**
🗣️ `BottomCenter            ` n= 269 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `TopCenter               ` n= 9 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**022\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_21\_\_1**
🗣️ `Default                 ` n= 151 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 85 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italic                  ` n= 17 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 10 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback Italics       ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**023\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_22\_\_1**
🗣️ `Default                 ` n= 237 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 9 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Top                     ` n= 1 pos= 0 | heur=NIEPEWNE prawda=DIALOG ❓

**024\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_23\_\_1**
🗣️ `Default                 ` n= 170 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 7 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**025\_\_\_SubsPlease\_\_Toujima_Tanzaburou_wa_Kamen_Rider_ni_Naritai\_-\_24\_\_1**
🗣️ `BottomCenter            ` n= 183 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `TopCenter               ` n= 9 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ

**026\_\_\_SubsPlease\_\_Vigilante\_-_Boku_no_Hero_Academia_Illegals_S2_-_07_\_**
🗣️ `flashback               ` n= 288 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback italics       ` n= 12 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `main                    ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_Verdana            ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_TimesNewRoman      ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `italics                 ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashbacktop            ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `overlap                 ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**027\_\_\_SubsPlease\_\_Vigilante\_-_Boku_no_Hero_Academia_Illegals_S2_-_08_\_**
🗣️ `flashback               ` n= 214 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `main                    ` n= 67 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback italics       ` n= 24 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_Verdana            ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_TimesNewRoman      ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_TrebuchetMS        ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_Arial              ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**028\_\_\_SubsPlease\_\_Vigilante\_-_Boku_no_Hero_Academia_Illegals_S2_-_09_\_**
🗣️ `main                    ` n= 340 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `top                     ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_Verdana            ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_TimesNewRoman      ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_Arial              ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_TrebuchetMS        ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅

**029\_\_\_SubsPlease\_\_Yuusha_no_Kuzu\_-_02\_\_1080p\_\_\_21A8CA53_.mkv.ass**
🗣️ `Default                 ` n= 153 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 119 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_generic            ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `flashback               ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `top                     ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**030\_\_\_shisha\_\_Jigokuraku_2nd_Season\_-\_09.mkv.ass**
🗣️ `Jigokuraku              ` n= 225 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Jigokuraku - Myśli      ` n= 50 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Kasukana Hana           ` n= 25 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Jigokuraku - Alt        ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅

**031\_\_\_lycoris.cafe\_\_Busamen_Gachi_Fighter\_-_5\_\_1080p_.mkv.ass**
🗣️ `Default                 ` n= 253 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 74 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `default - top           ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `eptitle                 ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default top             ` n= 1 pos= 0 | heur=DIALOG prawda=? —
🗣️ `flashback italics       ` n= 1 pos= 0 | heur=DIALOG prawda=? —
🔇 `handwriting             ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**032\_\_\_lycoris.cafe\_\_Busamen_Gachi_Fighter\_-_06\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 273 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 74 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `trebuchet-black-grey box` n= 7 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default - top           ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `eptitle                 ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default top             ` n= 1 pos= 0 | heur=DIALOG prawda=? —
🔇 `arial                   ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**036\_\_\_Erai-raws\_\_Arifureta_Shokugyou_de_Sekai_Saikyou_3rd_Season\_-_09_**
🗣️ `Default                 ` n= 294 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `On Top                  ` n= 2 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**037\_\_\_Erai-raws\_\_Arifureta_Shokugyou_de_Sekai_Saikyou_3rd_Season\_-_10_**
🗣️ `Default                 ` n= 266 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `On Top                  ` n= 4 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ

**038\_\_\_SubsPlease\_\_One_Room\_\_Hiatari_Futsuu\_\_Tenshi-tsuki\_-_01\_\_1080p_\_**
🗣️ `Default                 ` n= 305 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 70 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_generic            ` n= 28 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `top                     ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italicstop              ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**039\_\_\_SubsPlease\_\_Tsue_to_Tsurugi_no_Wistoria\_-_02\_\_1080p\_\_\_53E76DBF_.**
🗣️ `Default                 ` n= 225 pos= 8 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Italics          ` n= 39 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 21 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 15 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback - Top         ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top + Italics    ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**040\_\_\_SubsPlease\_\_Tsue_to_Tsurugi_no_Wistoria\_-_03\_\_1080p\_\_\_6D17C648_.**
🗣️ `Main                    ` n= 186 pos= 12 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Italics          ` n= 54 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 21 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 12 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback - Italics     ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**041\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_01\_\_1080p\_\_\_AB352C1E_.mk**
🗣️ `Default                 ` n= 302 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 47 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 22 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultTop              ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**042\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_02\_\_1080p\_\_\_26052902_.mk**
🗣️ `Default                 ` n= 315 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 21 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_generic            ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `flashback               ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**043\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_03\_\_1080p\_\_\_263098CD_.mk**
🗣️ `Default                 ` n= 305 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 21 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 20 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_generic            ` n= 3 pos= 67 | heur=ZNAK prawda=ZNAK ✅

**044\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_04\_\_1080p\_\_\_203FDCCB_.mk**
🗣️ `Default                 ` n= 304 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 15 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultItalics          ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_generic            ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**045\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_05\_\_1080p\_\_\_CCA86BE8_.mk**
🗣️ `Default                 ` n= 228 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 75 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 28 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_generic            ` n= 13 pos= 85 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**046\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_06\_\_1080p\_\_\_29104EC1_.mk**
🗣️ `Default                 ` n= 299 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_generic            ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**047\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_07\_\_1080p\_\_\_EF05B5B1_.mk**
🗣️ `Default                 ` n= 294 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 14 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_generic            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**048\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_08\_\_1080p\_\_\_6DCDA080_.mk**
🗣️ `Default                 ` n= 191 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 67 pos= 94 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 43 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_generic            ` n= 18 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultTop              ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `FlashbackItalics        ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**049\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_09\_\_1080p\_\_\_90221C7B_.mk**
🗣️ `Default                 ` n= 276 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 13 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_generic            ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultTop              ` n= 1 pos= 0 | heur=DIALOG prawda=? —

**050\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_10\_\_1080p\_\_\_9ADB96A4_.mk**
🗣️ `Default                 ` n= 251 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 23 pos= 91 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 21 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 14 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**051\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_11\_\_1080p\_\_\_83B90909_.mk**
🗣️ `Default                 ` n= 230 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 53 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 36 pos= 89 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultItalics          ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**052\_\_\_SubsPlease\_\_Bartender\_-_Kami_no_Glass_-_12\_\_1080p\_\_\_F5327758_.mk**
🗣️ `Default                 ` n= 262 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultItalics          ` n= 19 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 12 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**071\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_04\_\_1080p\_\_\_C5C682F5**
🗣️ `Default                 ` n= 220 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 69 pos= 71 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 62 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bottom_Text             ` n= 26 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - Top           ` n= 20 pos= 5 | heur=DIALOG prawda=DIALOG ✅
🔇 `Handwritten_Borderless  ` n= 10 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**072\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_05\_\_1080p\_\_\_FF8F000F**
🗣️ `Default                 ` n= 307 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 40 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 37 pos= 95 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - Top           ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Character_Profile       ` n= 2 pos= 50 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Handwritten_Borderless  ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**073\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_06\_\_1080p\_\_\_714C07B8**
🗣️ `Default                 ` n= 376 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 13 pos= 92 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default - Top           ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Handwritten_Borderless  ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**074\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_07\_\_1080p\_\_\_CEBAED9F**
🗣️ `Default                 ` n= 199 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 71 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 35 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 12 pos= 67 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback_Italics       ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default - Top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Handwritten_Borderless  ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**075\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_08\_\_1080p\_\_\_7117C442**
🗣️ `Default                 ` n= 178 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 175 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 15 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 10 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback_Italics       ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Character_Profile       ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Handwritten_Borderless  ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - Top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**076\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_09\_\_1080p\_\_\_1E97A8FC**
🗣️ `Default                 ` n= 227 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 129 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 36 pos= 94 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback_Italics       ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default - Top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**077\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_10\_\_1080p\_\_\_1E97A8FC**
🗣️ `Default                 ` n= 295 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - Top           ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**078\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_11\_\_1080p\_\_\_AB4856C7**
🗣️ `Default                 ` n= 262 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 11 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 10 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default - Top           ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Handwritten_Borderless  ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `Character_Profile       ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `End_Title               ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**079\_\_\_SubsPlease\_\_Kumichou_Musume_to_Sewagakari\_-\_12\_\_1080p\_\_\_E52FA423**
🗣️ `Default                 ` n= 259 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 75 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 11 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback_Italics       ` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Bordered_TopSign        ` n= 7 pos= 57 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - Top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Handwritten_Borderless  ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Mid_Title               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**080\_\_R14.mkv.ass**
🗣️ `Re: Zero III            ` n= 128 pos= 2 | heur=DIALOG prawda=? —
🗣️ `Re: Zero III - Retrospek` n= 98 pos= 1 | heur=DIALOG prawda=? —
🗣️ `Re: Zero III - Myśli    ` n= 40 pos= 0 | heur=DIALOG prawda=? —
🔇 `NOX LUX by MYTH & ROID  ` n= 18 pos= 56 | heur=ZNAK prawda=? —
🗣️ `Re: Zero III - Retrospek` n= 3 pos= 0 | heur=DIALOG prawda=? —
🔇 `Znaki                   ` n= 2 pos=100 | heur=ZNAK prawda=? —
🗣️ `Re: Zero III - Alter    ` n= 1 pos= 0 | heur=DIALOG prawda=? —

**081\_\_R15.mkv.ass**
🗣️ `Re: Zero III            ` n= 324 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🔇 `Reweave by Konomi Suzuki` n= 19 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Reweave by Konomi Suzuki` n= 19 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Re: Zero III - Retrospek` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Re: Zero III - Alter    ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Re: Zero III - Myśli    ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**082\_\_10.mkv.ass**
🗣️ `Default                 ` n= 263 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**083\_\_11.mkv.ass**
🗣️ `Default                 ` n= 360 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**085\_\_7.mkv.ass**
🗣️ `Default                 ` n= 305 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**086\_\_8.mkv.ass**
🗣️ `Default                 ` n= 293 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**087\_\_9.mkv.ass**
🗣️ `Default                 ` n= 282 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**088\_\_Seikon_no_Qwaser_S01E01.mkv.ass**
🗣️ `Default                 ` n= 301 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Note                    ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**089\_\_Seikon_no_Qwaser_S01E02.mkv.ass**
🗣️ `Default                 ` n= 303 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**090\_\_Seikon_no_Qwaser_S01E03.mkv.ass**
🗣️ `Default                 ` n= 287 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**091\_\_Seikon_no_Qwaser_S01E04.mkv.ass**
🗣️ `Default                 ` n= 296 pos= 4 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**092\_\_Seikon_no_Qwaser_S01E05.mkv.ass**
🗣️ `Default                 ` n= 292 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Note                    ` n= 2 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**093\_\_Seikon_no_Qwaser_S01E06.mkv.ass**
🗣️ `Default                 ` n= 338 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 6 pos= 67 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Note                    ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**094\_\_Seikon_no_Qwaser_S01E07.mkv.ass**
🗣️ `Default                 ` n= 298 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 4 pos= 75 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Note                    ` n= 2 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**095\_\_Seikon_no_Qwaser_S01E08.mkv.ass**
🗣️ `Default                 ` n= 296 pos= 4 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 1 pos= 0 | heur=DIALOG prawda=? —

**096\_\_Seikon_no_Qwaser_S01E09.mkv.ass**
🗣️ `Default                 ` n= 310 pos= 4 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**097\_\_Seikon_no_Qwaser_S01E10.5_OVA.mkv.ass**
🗣️ `Default                 ` n= 301 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default-alt             ` n= 16 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `ED Romaji               ` n= 14 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `OP Romaji               ` n= 14 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `OP Kanji                ` n= 13 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `OP English              ` n= 13 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `ED Kanji                ` n= 12 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `ED English              ` n= 12 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Signs                   ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Note                    ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Signs2                  ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**098\_\_Seikon_no_Qwaser_S01E10.mkv.ass**
🗣️ `Default                 ` n= 265 pos= 4 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Note                    ` n= 3 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**099\_\_Seikon_no_Qwaser_S01E11.mkv.ass**
🗣️ `Default                 ` n= 296 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `BloodSign               ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**100\_\_Seikon_no_Qwaser_S01E12.mkv.ass**
🗣️ `Default                 ` n= 315 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**101\_\_Seikon_no_Qwaser_S01E13.mkv.ass**
🗣️ `Default                 ` n= 327 pos= 3 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**102\_\_Seikon_no_Qwaser_S01E14.mkv.ass**
🗣️ `Default                 ` n= 278 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 12 pos=100 | heur=ZNAK prawda=ZNAK ✅

**103\_\_Seikon_no_Qwaser_S01E15.mkv.ass**
🗣️ `Default                 ` n= 215 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅

**104\_\_Seikon_no_Qwaser_S01E16.mkv.ass**
🗣️ `Default                 ` n= 288 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**105\_\_Seikon_no_Qwaser_S01E17.mkv.ass**
🗣️ `Default                 ` n= 246 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**106\_\_Seikon_no_Qwaser_S01E18.mkv.ass**
🗣️ `Default                 ` n= 314 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default-alt             ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**107\_\_Seikon_no_Qwaser_S01E19.mkv.ass**
🗣️ `Default                 ` n= 266 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**108\_\_Seikon_no_Qwaser_S01E20.mkv.ass**
🗣️ `Default                 ` n= 271 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅

**109\_\_Seikon_no_Qwaser_S01E21.mkv.ass**
🗣️ `Default                 ` n= 273 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default-alt             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**110\_\_Seikon_no_Qwaser_S01E22.mkv.ass**
🗣️ `Default                 ` n= 276 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**111\_\_Seikon_no_Qwaser_S01E23.mkv.ass**
🗣️ `Default                 ` n= 295 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅

**112\_\_Seikon_no_Qwaser_S01E24.mkv.ass**
🗣️ `Default                 ` n= 267 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `OP Romaji               ` n= 26 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `OP English              ` n= 25 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `OP Kanji                ` n= 23 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Signs                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**113\_\_Seikon_no_Qwaser_S02E01.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 285 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 20 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji OP                ` n= 19 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji ED                ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Seikon no Qwaser II sign` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default                 ` n= 3 pos= 0 | heur=DIALOG prawda=? —
🔇 `SubDesu Logo            ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**114\_\_Seikon_no_Qwaser_S02E02.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 261 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 20 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji OP                ` n= 19 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji ED                ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Default                 ` n= 4 pos= 0 | heur=DIALOG prawda=? —
🔇 `SubDesu Logo            ` n= 2 pos=100 | heur=ZNAK prawda=? —
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**115\_\_Seikon_no_Qwaser_S02E03.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 265 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 20 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji OP                ` n= 19 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji ED                ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Default                 ` n= 3 pos= 0 | heur=DIALOG prawda=? —
🔇 `Seikon no Qwaser II sign` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `SubDesu Logo            ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**116\_\_Seikon_no_Qwaser_S02E04.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 298 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 20 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji OP                ` n= 19 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji ED                ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default                 ` n= 2 pos= 0 | heur=DIALOG prawda=? —
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**117\_\_Seikon_no_Qwaser_S02E05.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 286 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 20 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji OP                ` n= 19 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji ED                ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos= 50 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default                 ` n= 2 pos= 0 | heur=DIALOG prawda=? —
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**118\_\_Seikon_no_Qwaser_S02E06.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 302 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 20 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji OP                ` n= 19 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Kanji ED                ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 15 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default                 ` n= 1 pos= 0 | heur=DIALOG prawda=? —

**119\_\_Seikon_no_Qwaser_S02E07.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 266 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos= 50 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**120\_\_Seikon_no_Qwaser_S02E08.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 354 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Default                 ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**121\_\_Seikon_no_Qwaser_S02E09.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 315 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Default                 ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**122\_\_Seikon_no_Qwaser_S02E10.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 339 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Seikon no Qwaser II sign` n= 25 pos= 92 | heur=ZNAK prawda=ZNAK ✅
🔇 `Romanji OP              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Seikon no Qwaser II sign` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `SubDesu Logo            ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos= 50 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**123\_\_Seikon_no_Qwaser_S02E11.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 354 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Seikon no Qwaser II sign` n= 11 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**124\_\_Seikon_no_Qwaser_S02E12.mkv.ass**
🗣️ `Seikon no Qwaser II Dial` n= 331 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Romanji OP              ` n= 14 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English OP              ` n= 13 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Romanji ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `English ED              ` n= 12 pos= 0 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `SubDesu Logo            ` n= 5 pos= 80 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Seikon no Qwaser II sign` n= 1 pos= 0 | heur=ZNAK prawda=? —

**125\_\_\_lycoris.cafe\_\_NUKITASHI_THE_ANIMATION\_-_08\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 338 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Text                    ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default - top           ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**126\_\_\_lycoris.cafe\_\_NUKITASHI_THE_ANIMATION\_-_09\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 336 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Text                    ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default - top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**127\_\_\_lycoris.cafe\_\_NUKITASHI_THE_ANIMATION\_-_10\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 345 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🗣️ `default - top           ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Text                    ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**128\_\_\_lycoris.cafe\_\_NUKITASHI_THE_ANIMATION\_-_11\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 335 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default - top           ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**129\_\_\_Erai-raws\_\_Sanda\_-\_01\_\_1080p_AMZN_WEBRip_HEVC_EAC3\_\_MultiSub\_\_7E**
🗣️ `Default                 ` n= 455 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**130\_\_\_Erai-raws\_\_Sanda\_-\_02\_\_1080p_AMZN_WEBRip_HEVC_EAC3\_\_MultiSub\_\_9B**
🗣️ `Default                 ` n= 457 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**131\_\_\_Erai-raws\_\_Sanda\_-\_03\_\_1080p_AMZN_WEB-DL_AVC_EAC3\_\_MultiSub\_\_31A**
🗣️ `Default                 ` n= 416 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**132\_\_\_Erai-raws\_\_Sanda\_-\_04\_\_1080p_AMZN_WEB-DL_AVC_EAC3\_\_MultiSub\_\_C6C**
🗣️ `Default                 ` n= 385 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**133\_\_\_Erai-raws\_\_Sanda\_-\_05\_\_1080p_AMZN_WEB-DL_AVC_EAC3\_\_MultiSub\_\_B2A**
🗣️ `Default                 ` n= 429 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**134\_\_\_Erai-raws\_\_Sanda\_-\_06\_\_1080p_AMZN_WEB-DL_AVC_EAC3\_\_MultiSub\_\_6F8**
🗣️ `Default                 ` n= 416 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**135\_\_\_Erai-raws\_\_Sanda\_-\_07\_\_1080p_AMZN_WEB-DL_AVC_EAC3\_\_MultiSub\_\_8AA**
🗣️ `Default                 ` n= 435 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**136\_\_\_shisha\_\_Haite_Kudasai_Takamine-san\_-\_02.mkv.ass**
🗣️ `Takamine                ` n= 185 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Takamine - Myśli        ` n= 93 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 28 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `Masami Okui - Baby Baby ` n= 20 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🔇 `Eyecatch                ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Takamine - Alt          ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_11988_145_Please_Pu` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_6229_38_Student_Cou` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Episode Title           ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅

**137\_\_\_lycoris.cafe\_\_Class_de_2-banme_ni_Kawaii_Onnanoko_to_Tomodachi_n**
🗣️ `Default                 ` n= 284 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultItalics          ` n= 42 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 14 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Czat                    ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**138\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_01\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 277 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 60 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 21 pos= 95 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `TS                      ` n= 15 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Góra              ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**139\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_02\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 247 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 77 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Furry Góra              ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 9 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**140\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_03\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 251 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 51 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 23 pos=100 | heur=ZNAK prawda=DIALOG 🔴CICHY
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Furry Góra              ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**141\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_04\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 264 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 48 pos= 98 | heur=ZNAK prawda=DIALOG 🔴CICHY
🗣️ `Furry Kursywa           ` n= 45 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 38 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Furry Góra              ` n= 17 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**142\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_05\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 304 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 73 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 37 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Furry Góra              ` n= 14 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 11 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**143\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_06\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 236 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 59 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 37 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 13 pos= 92 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Góra              ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**144\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_07\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 238 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 57 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 37 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**145\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_08\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 261 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 64 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Kursywa           ` n= 44 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 6 pos= 83 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Góra              ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**146\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_09\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 334 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 41 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Furry Góra              ` n= 12 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `TS                      ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**147\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_10\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 306 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 42 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 37 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 8 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Góra              ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**148\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_11\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 301 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `TS                      ` n= 64 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Kursywa           ` n= 35 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 19 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `Furry Góra              ` n= 4 pos= 0 | heur=NIEPEWNE prawda=DIALOG ❓
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**149\_\_\_Fuji\_\_Kimi_to_Koete_Koi_ni_Naru\_-_12\_\_1080p_.mkv.ass**
🗣️ `Furry                   ` n= 269 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Furry Kursywa           ` n= 46 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Opening                 ` n= 30 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Ending                  ` n= 20 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `Znaki                   ` n= 8 pos= 88 | heur=ZNAK prawda=ZNAK ✅
🔇 `TS                      ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Furry Góra              ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Kredki                  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅

**150\_\_\_SubsPlease\_\_Kami_no_Niwatsuki_Kusunoki-tei\_-\_01\_\_720p\_\_\_F6575706**
🗣️ `Default                 ` n= 343 pos= 7 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 26 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default Top             ` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**151\_\_\_SubsPlease\_\_Kami_no_Niwatsuki_Kusunoki-tei\_-\_02\_\_1080p\_\_\_59C6C03**
🗣️ `Default                 ` n= 356 pos= 5 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 11 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Default Top             ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**152\_\_\_SubsPlease\_\_Mata_Korosarete_Shimatta_no_desu_ne\_\_Tantei-sama\_-\_0**
🗣️ `Default                 ` n= 271 pos= 14 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 43 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Top                     ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**153\_\_\_SubsPlease\_\_Mata_Korosarete_Shimatta_no_desu_ne\_\_Tantei-sama\_-\_0**
🗣️ `Default                 ` n= 264 pos= 11 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 37 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Top                     ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**154\_\_\_SubsPlease\_\_Shibou_Yuugi_de_Meshi_wo_Kuu.\_-\_07\_\_1080p\_\_\_144627FF**
🗣️ `main                    ` n= 114 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 22 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 20 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback italics       ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `top                     ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**155\_\_\_SubsPlease\_\_Shibou_Yuugi_de_Meshi_wo_Kuu.\_-\_08\_\_1080p\_\_\_93FFCD30**
🗣️ `main                    ` n= 178 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 17 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `top                     ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_Georgia            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**156\_\_\_SubsPlease\_\_Shibou_Yuugi_de_Meshi_wo_Kuu.\_-\_09\_\_1080p\_\_\_DE87BF78**
🗣️ `main                    ` n= 163 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italicstop              ` n= 12 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `top                     ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**157\_\_\_SubsPlease\_\_Shibou_Yuugi_de_Meshi_wo_Kuu.\_-\_10\_\_1080p\_\_\_6CB8E615**
🗣️ `italics                 ` n= 70 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 61 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback italics       ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `main                    ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashbackitalicstop     ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**158\_\_\_SubsPlease\_\_Shibou_Yuugi_de_Meshi_wo_Kuu.\_-\_11\_\_1080p\_\_\_F8ECA54A**
🗣️ `flashback               ` n= 77 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `main                    ` n= 72 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 26 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashbacktop            ` n= 16 pos= 0 | heur=DIALOG prawda=? —

**159\_\_\_SubsPlease\_\_Yomi_no_Tsugai\_-_02\_\_1080p\_\_\_81EC5E72_.mkv.ass**
🗣️ `Default                 ` n= 303 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 36 pos= 0 | heur=DIALOG prawda=PIOSENKA 🟡FALSZ
🔇 `sign_generic            ` n= 14 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `flashback               ` n= 11 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**160\_\_\_lycoris.cafe\_\_Mata_Korosarete_Shimatta_no_desu_ne_Tantei-sama\_-\_**
🗣️ `Default                 ` n= 294 pos= 9 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics top             ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `top                     ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**161\_\_\_shisha\_\_Tsue_to_Tsurugi_no_Wistoria_Season_2\_-\_01.mkv.ass**
🗣️ `Wistoria                ` n= 295 pos= 1 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 63 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Wistoria - Myśli        ` n= 44 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Wistoria - Alter        ` n= 12 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**162\_\_Gals_Can_t_Be_Kind_to_Otaku_S01E11_VOSTFR_1080p_WEB_x264_AAC\_-Tsu**
🗣️ `Default                 ` n= 284 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italique                ` n= 44 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign                    ` n= 24 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🗣️ `TiretsDefault           ` n= 16 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**163\_\_Gals_Can_t_Be_Kind_to_Otaku_S01E12_VOSTFR_1080p_WEB_x264_AAC\_-Tsu**
🗣️ `Default                 ` n= 222 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italique                ` n= 98 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Sign                    ` n= 15 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🗣️ `TiretsDefault           ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**164\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_01\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 294 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_34006_297_Circuit_B` n= 11 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Sign_Basic              ` n= 8 pos= 88 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text_Box       ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_12329_149_Solid    ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**165\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_02\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 285 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_4811_65_Electricity` n= 9 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Sign_Basic              ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text_Box       ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback_Italics       ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**166\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_03\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 200 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 47 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 16 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Acquired_Text_Box       ` n= 9 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_4811_65_Electricity` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback_Italics       ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**167\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_04\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 215 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 21 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_27936_262_Ethanol  ` n= 21 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 19 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Sign_Basic              ` n= 3 pos= 33 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Acquired_Text_Box       ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**168\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_05\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 266 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 16 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 6 pos= 67 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text_Box       ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**169\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_06\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 245 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_27936_262_Ethanol  ` n= 9 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Acquired_Text_Box       ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Flashback               ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_17052_152_Phosphate` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**170\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_07\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 233 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Acquired_Text_Box       ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**171\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_08\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 252 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_27936_262_Ethanol  ` n= 14 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Sign_Basic              ` n= 10 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text_Box       ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**172\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_09\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 245 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 16 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text_Box       ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_27936_262_Ethanol  ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**173\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_10\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 306 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 25 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_27936_262_Ethanol  ` n= 11 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text_Box       ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Acquired_Text           ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**174\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_11\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 239 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 18 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 8 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Time Setting            ` n= 1 pos=100 | heur=ZNAK prawda=? —
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**175\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_12\_\_1080p_CR_WEBRi**
🗣️ `Main                    ` n= 232 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 15 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Episode            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Next_Ep_Title           ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**176\_\_\_Erai-raws\_\_Dr_Stone\_-_Science_Future_Part_3_-\_13\_\_1080p_CR_WEB-D**
🗣️ `Main                    ` n= 221 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `sign_8958_97_Ramen      ` n= 28 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Italics                 ` n= 15 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 5 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Ep_Title                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**177\_\_\_Erai-raws\_\_Koori_no_Jouheki\_-\_09\_\_1080p_NF_WEB-DL_AVC_AAC\_\_Multi**
🗣️ `Default                 ` n= 374 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**178\_\_\_Erai-raws\_\_Koori_no_Jouheki\_-\_10\_\_1080p_NF_WEB-DL_AVC_AAC\_\_Multi**
🗣️ `Default                 ` n= 470 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**179\_\_\_Erai-raws\_\_Koori_no_Jouheki\_-\_11\_\_1080p_NF_WEB-DL_AVC_AAC\_\_Multi**
🗣️ `Default                 ` n= 422 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**180\_\_\_Erai-raws\_\_Koori_no_Jouheki\_-\_12\_\_1080p_NF_WEB-DL_AVC_AAC\_\_Multi**
🗣️ `Default                 ` n= 379 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**181\_\_\_Erai-raws\_\_Koori_no_Jouheki\_-\_13\_\_1080p_NF_WEB-DL_AVC_AAC\_\_Multi**
🗣️ `Default                 ` n= 404 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**182\_\_\_SubsPlease\_\_Class_de_2-banme_ni_Kawaii_Onnanoko_to_Tomodachi_ni\_**
🗣️ `Default                 ` n= 294 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `DefaultItalics          ` n= 33 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Signs                   ` n= 5 pos= 40 | heur=ZNAK prawda=ZNAK ✅
🗣️ `DefaultTop              ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `FlashbackTop            ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**183\_\_\_SubsPlease\_\_Himekishi_wa_Barbaroi_no_Yome\_-\_11\_\_1080p\_\_\_AB8767F9**
🗣️ `Main                    ` n= 283 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 21 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics - Top           ` n= 2 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Time/Setting            ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**184\_\_\_SubsPlease\_\_Himekishi_wa_Barbaroi_no_Yome\_-\_12\_\_1080p\_\_\_CB5DD8F1**
🗣️ `Main                    ` n= 251 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 31 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Main - Top              ` n= 22 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Time/Setting            ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Sign_Basic              ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅

**185\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_05\_\_1080p\_\_\_6706CE18_.mkv.**
🗣️ `Q1                      ` n= 389 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q0                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🗣️ `Q4                      ` n= 19 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q2                      ` n= 19 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q3                      ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q5                      ` n= 3 pos= 0 | heur=ZNAK prawda=ZNAK ✅
❓ `Q6                      ` n= 2 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
❓ `Q7                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**186\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_06\_\_1080p\_\_\_7DF701F0_.mkv.**
🗣️ `Q1                      ` n= 403 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q0                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🔇 `Q2                      ` n= 18 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Q3                      ` n= 16 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q4                      ` n= 12 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `Q7                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q6                      ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q5                      ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**187\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_07\_\_1080p\_\_\_8322CCD7_.mkv.**
🗣️ `Q1                      ` n= 359 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q0                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🗣️ `Q3                      ` n= 10 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q7                      ` n= 9 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q2                      ` n= 8 pos= 75 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q4                      ` n= 5 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q6                      ` n= 4 pos= 50 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q8                      ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
❓ `Q10                     ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q5                      ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q9                      ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**188\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_08\_\_1080p\_\_\_02B5FDFE_.mkv.**
🗣️ `Q0                      ` n= 369 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q1                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🗣️ `Q2                      ` n= 9 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q3                      ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q4                      ` n= 2 pos= 0 | heur=ZNAK prawda=ZNAK ✅
❓ `Q5                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**189\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_09\_\_1080p\_\_\_E2C845C1_.mkv.**
🗣️ `Q0                      ` n= 398 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q1                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🗣️ `Q2                      ` n= 16 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q7                      ` n= 3 pos= 67 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q4                      ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `Q5                      ` n= 2 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
❓ `Q8                      ` n= 2 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q10                     ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q3                      ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
❓ `Q6                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q11                     ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q9                      ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**190\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_10\_\_1080p\_\_\_EAF81DE3_.mkv.**
🗣️ `Q1                      ` n= 414 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q0                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🔇 `Q5                      ` n= 9 pos= 89 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q3                      ` n= 8 pos= 50 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Q2                      ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q4                      ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Q7                      ` n= 1 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ
❓ `Q8                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q6                      ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**191\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_11\_\_1080p\_\_\_288E8C79_.mkv.**
🗣️ `Q1                      ` n= 426 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q0                      ` n= 44 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🔇 `Q2                      ` n= 16 pos= 56 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Q3                      ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q4                      ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `Q6                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q5                      ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅

**192\_\_\_SubsPlease\_\_Isekai_Nonbiri_Nouka_S2\_-_12\_\_1080p\_\_\_12C3D6B8_.mkv.**
🗣️ `Q1                      ` n= 466 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `Q10                     ` n= 33 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
❓ `Q0                      ` n= 20 pos= 0 | heur=NIEPEWNE prawda=PIOSENKA ❓
🗣️ `Q3                      ` n= 19 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Q5                      ` n= 7 pos= 71 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q2                      ` n= 2 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q4                      ` n= 2 pos= 50 | heur=ZNAK prawda=ZNAK ✅
❓ `Q6                      ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🔇 `Q7                      ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q8                      ` n= 1 pos= 0 | heur=ZNAK prawda=ZNAK ✅
🔇 `Q9                      ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**193\_\_\_SubsPlease\_\_Kill_Ao\_-_09\_\_1080p\_\_\_281C95F2_.mkv.ass**
🗣️ `Default                 ` n= 363 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `On Top                  ` n= 14 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ
🗣️ `Italics                 ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**194\_\_\_SubsPlease\_\_Kill_Ao\_-_10\_\_1080p\_\_\_5C9E744A_.mkv.ass**
🗣️ `Default                 ` n= 371 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `On Top                  ` n= 16 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓
🗣️ `Italics                 ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**195\_\_\_SubsPlease\_\_Kill_Ao\_-_11\_\_1080p\_\_\_CBC70D81_.mkv.ass**
🗣️ `Default                 ` n= 421 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `On Top                  ` n= 17 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**196\_\_\_SubsPlease\_\_Kill_Ao\_-_12\_\_1080p\_\_\_9C22A8A0_.mkv.ass**
🗣️ `Default                 ` n= 422 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `On Top                  ` n= 9 pos= 0 | heur=DIALOG prawda=ZNAK 🟡FALSZ
🗣️ `Italics                 ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**197\_\_\_SubsPlease\_\_Ponkotsu_Fuuki_Iin_to_Skirt-take_ga_Futekisetsu_na_J**
🗣️ `Main                    ` n= 338 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 103 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 48 pos= 85 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 17 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback               ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics - Top           ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Flashback - Top         ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Narration               ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**198\_\_\_SubsPlease\_\_Ponkotsu_Fuuki_Iin_to_Skirt-take_ga_Futekisetsu_na_J**
🗣️ `Main                    ` n= 369 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics                 ` n= 32 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 27 pos= 93 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Main - Top              ` n= 13 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Narration               ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Italics - Top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅

**199\_\_\_lycoris.cafe\_\_Honzuki_no_Gekokujou-_Ryoushu_no_Youjo_-_9\_\_1080p_**
🗣️ `Default                 ` n= 275 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 38 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `ep title                ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - top           ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign                    ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `eyecatch                ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
❓ `illustration_by_        ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**200\_\_\_lycoris.cafe\_\_Honzuki_no_Gekokujou_S4\_-_07\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 244 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 30 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign                    ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `flashback               ` n= 6 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `ep title                ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Default - top           ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `eyecatch                ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `default_top             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics_top             ` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
❓ `illustration_by_        ` n= 1 pos= 0 | heur=NIEPEWNE prawda=ZNAK ❓

**201\_\_\_lycoris.cafe\_\_Honzuki_no_Gekokujou_S4\_-_08\_\_source-mkv_.mkv.ass**
🗣️ `Default                 ` n= 239 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `italics                 ` n= 55 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `flashback               ` n= 7 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `ep title                ` n= 4 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `eyecatch                ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `selfplug                ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `title                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sfx                     ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `illustration_by_        ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**202\_\_\_lycoris.cafe\_\_Tensei_Shitara_Slime_Datta_Ken_4th_Season\_-\_9\_\_108**
🗣️ `Tensura - Podstawowe    ` n= 250 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Tensura - Kursywa       ` n= 56 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Tensura - Górne Kursywa ` n= 17 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Tensura - Górne         ` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Creditsy                ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Tytuł Odcinka           ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Znaki/podpisy           ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Tytuł Następnego Odcinka` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Tytuł                   ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**204\_\_\_FrixySubs\_\_Dr._STONE_-\_S04E25\_\_1080p_CR_WEB-DL_H.264_AAC\_\_\_Napis**
🔇 `Rysunki                 ` n=6000 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Dr.Stone - Podstawowe   ` n= 282 pos= 4 | heur=DIALOG prawda=DIALOG ✅
🔇 `Dr. Stone - Okienka     ` n= 22 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Dr. Stone OP2 Tłumaczeni` n= 16 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🔇 `sign_34006_297_Circuit_B` n= 11 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Disclaimer              ` n= 6 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Dr.Stone - Kursywa      ` n= 4 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Sign_Basic              ` n= 3 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `Dr Stone - Zapowiedź    ` n= 2 pos=100 | heur=ZNAK prawda=ZNAK ✅
🔇 `sign_12329_149_Solid    ` n= 1 pos=100 | heur=ZNAK prawda=ZNAK ✅

**205\_\_\_shisha\_\_Classroom_of_the_Elite_S4\_-_16\_\_1080p_.mkv.ass**
🔇 `MONSTER -  Eir Aoi [PL] ` n= 387 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Classroom of the Elite  ` n= 333 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `MONSTER -  Eir Aoi [PL] ` n= 58 pos=100 | heur=ZNAK prawda=PIOSENKA ✅
🗣️ `Classroom of the Elite -` n= 17 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🔇 `Znaki                   ` n= 7 pos=100 | heur=ZNAK prawda=ZNAK ✅
🗣️ `Classroom of the Elite -` n= 3 pos= 0 | heur=DIALOG prawda=DIALOG ✅
🗣️ `Classroom of the Elite -` n= 1 pos= 0 | heur=DIALOG prawda=DIALOG ✅
