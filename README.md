# <p align="center">✨ MM_AVH Working Space ✨</p>

<p align="center">
  <strong>Multimedia Magic – Audio Visual Heaven</strong><br>
  Automatyczne lektorowanie wideo, tłumaczenie napisów i tworzenie audiobooków
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

## 📸 Demo

<img src="./assets/img/mm_avh_working_space.gif" alt="MM_AVH Demo" width="100%">

## ✨ Funkcje

| Funkcja | Opis |
|---------|------|
| 🎬 Ekstrakcja | Wyciąganie audio i napisów z MKV |
| 📝 Konwersja | ASS → SRT, podział według stylów |
| 🌍 Tłumaczenie | Google Translate, DeepL, ChatGPT |
| 🎤 Lektorowanie | Edge TTS, Ivona, Harpo |
| 📚 Audiobooki | Generowanie z TXT/SRT |
| 🎥 Scalanie | MKV z lektorem lub wypalone MP4 |

## 🚀 Instalacja i uruchomienie

```bash
git clone https://github.com/MattyMroz/mm_avh_working_space.git
cd mm_avh_working_space
uv sync
uv run start.py
```

Lub kliknij `run_mm_avh.bat`

## 📖 Jak używać

1. Wrzuć **plik MKV** do `working_space/`
2. Uruchom `uv run start.py`
3. Odpowiadaj na pytania (`T`/`Y` = tak)
4. Wyniki w `working_space/output/`

**Audiobook:** Wrzuć `.txt` lub `.srt` do `working_space/temp/`

## 📁 Struktura

```
mm_avh_working_space/
├── bin/                    # FFmpeg, MKVToolNix, Balabolka
├── data/                   # Konfiguracja i ustawienia
├── modules/                # Główne moduły programu
├── utils/                  # Narzędzia pomocnicze
├── working_space/          # ⚡ FOLDER ROBOCZY
│   ├── output/             # Wyniki
│   └── temp/               # Pliki tymczasowe
├── start.py                # ⚡ PUNKT WEJŚCIA
└── pyproject.toml          # Zależności
```

## 🎤 Głosy TTS

| Głos | Silnik | Typ |
|------|--------|-----|
| Zofia | Edge TTS | Online (darmowy) |
| Marek | Edge TTS | Online (darmowy) |
| Agnieszka | Ivona | Systemowy |
| Zosia | Harpo | Systemowy |

## ⚙️ Konfiguracja

Ustawienia zapisują się automatycznie w `data/settings.json`.

Przy pierwszym uruchomieniu program zapyta o:
- Translator (Google/DeepL/ChatGPT)
- Głos TTS
- Szybkość i głośność
- Format wyjściowy

## 🔧 Edge TTS - lepsza jakość

Po `uv sync` zmień w pliku `edge_tts/communicate.py` (linia ~407):
```
48kbitrate → 96kbitrate
```

Znajdź plik:
```bash
uv run python -c "import edge_tts, os; print(os.path.dirname(edge_tts.__file__))"
```

## 🔗 Powiązane projekty

- [MM_AVH Media Players](https://github.com/MattyMroz/mm_avh_media_players)
- [MM_AVH Web Players](https://github.com/MattyMroz/mm_avh_web_players)
- [11Labs TTS Colab](https://github.com/MattyMroz/11Labs_TTS_Colab_Shere)

## 📄 Licencja

[MIT](LICENSE) © Mateusz Mróz

## 📧 Kontakt

[![Email](https://img.shields.io/badge/Email-mateuszmroz001%40gmail.com-blue?style=for-the-badge&logo=gmail)](mailto:mateuszmroz001@gmail.com)
