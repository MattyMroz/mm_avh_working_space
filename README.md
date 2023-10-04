# <p align="center">✨MM_AVH✨<br>✨WORKING SPACE✨</p>

## Spis Treści

- [📝 Krótki Opis](#-krótki-opis)
- [📦 Zawartość](#-zawartość)
- [🔗 Linki](#-linki)
- [🔍 Wymagania](#-wymagania)
- [⚡ Instalacja](#-instalacja)
- [🔄 Aktualizacje](#-aktualizacje)
- [📝 Opis](#-opis-programów)
- [📸 Demonstracja](#-demonstracja)
- [📌 Uwagi](#-uwagi)
- [📄 Licencja](#-licencja)
- [📧 Kontakt](#-kontakt)

## 📝 Krótki Opis

**Multimedia Magic – Audio Visual Heaven (MM_AVH)** to zestaw narzędzi do przetwarzania i ulepszania multimediów. Repozytorium **_MM_AVH Working Space_** służy jako przestrzeń robocza do ciągłego pobierania, ulepszania i generowania multimediów.

**MM_AVH** składa się z wielu programów, które są stosowane sekwencyjnie, umożliwiając wielowarstwowe przetwarzanie multimediów. Narzędzia obejmują m.in:

- playery, readery, konwertery, edytory, wizualizatory, analizatory, generatory, itp.
- skalowanie
- interpolację
- zarządzanie napisami
- lektorowanie wideo (dubbingowanie w przyszłości)
- tworzenie audiobooków
- automatyczne tłumaczenie tekstów
  i wiele innych.

Celem **MM_AVH** jest udostępnienie zaawansowanych, łatwych w użyciu narzędzi do manipulacji multimediów. **_MM_AVH Working Space_** jest częścią większego projektu, który ma na celu udostępnienie darmowego dostępu do multimediów i ułatwienie ich ulepszania i modyfikacji. Praca nad ulepszaniem **MM_AVH** jest ciągła, a repozytorium jest miejscem, gdzie te ulepszenia są opracowywane i testowane. Projekt **MM_AVH** skupia się również na odkrywaniu i dzieleniu się programami, które mogą poprawić jakość i wygodę odbioru multimediów.

## 📦 Zawartość

Projekt **MM_AVH Working Space** składa się z następujących głównych plików i folderów:

- `assets`: Folder zawierający prezentacje i zrzuty ekranu. Ten folder nie jest niezbędny do działania projektu i może być usunięty.
- `bin`: W tym folderze znajdują się wszystkie pliki wykonywalne (exe) oraz modele używane w projekcie. Podfoldery obejmują:
  - `balabolka`
  - `esrgan`
  - `ffmpeg`
  - `mkvtoolnix`
  - `models`
- `data`: Folder zawierający proste ustawienia programu terminalowego.
- `installation.zip`: Plik zawierający instalatory głosów systemowych.
- `modules`: Moduły stworzone specjalnie dla tego projektu.
- `tests`: Folder zawierający testy nowych rozwiązań. Ten folder nie jest niezbędny do działania projektu i może być usunięty.
- `utils`: Moduły, które mogą być używane w innych projektach.
- `working_space`: Folder roboczy, do którego przekazujemy pliki do przetworzenia. Zawiera podfoldery `output` i `temp`, które zawierają odpowiednio wyniki przetwarzania i pliki tymczasowe.
- `constants.py`: Plik zawierający stałe ustawienia programu, takie jak ścieżki do folderów i kolorystyka.
- `LICENSE`: Plik zawierający informacje o licencji projektu.
- `README.md`: Plik zawierający wszystkie informacje, które powinieneś wiedzieć o projekcie.
- `start.py`: Plik, który uruchamia proces przetwarzania.
- `requirements.txt`: Plik zawierający listę bibliotek wymaganych do działania projektu.

Struktura folderów projektu wygląda następująco:

```
mm_avh_working_space
├───assets ... ❌
├───bin
│   ├───balabolka
│   ├───esrgan
│   ├───ffmpeg ...
│   │   ├───bin
│   ├───mkvtoolnix ...
│   └───models
├───data
├───modules
├───tests ❌
├───utils
└───working_space ❗
    ├───output
    └───temp
        ├───alt_subs
        └───main_subs
```

Pliki na poziomie głównym to:

- `constants.py`
- `installation.zip`❗
- `LICENSE`
- `README.md`
- `requirements.txt` ❗
- `start.py` ❗

❌ - zbędne po zapoznaiu się z urzwyaniem

❗ - ważne

## 🔗 Linki

<!-- - [Strona Główna - do zrobienia❗❗❗](https://mattymroz.github.io/mm_avh/) -->

- [Media Players](https://github.com/MattyMroz/mm_avh_media_players)
- [Web Players](https://github.com/MattyMroz/mm_avh_web_players)
- [11Labs_TTS_Colab_Shere](https://github.com/MattyMroz/11Labs_TTS_Colab_Shere)

## 🔍 Wymagania

Aby korzystać z **MM_AVH Working Space**, musisz spełnić następujące wymagania:

- System operacyjny: Windows. Program nie jest przeznaczony do użytku na innych systemach operacyjnych, takich jak Linux czy MacOS.
- Python: Wersja 10 lub nowsza. Możesz pobrać najnowszą wersję Pythona z [oficjalnej strony Pythona](https://www.python.org/downloads/).
- FFmpeg: Musi być zainstalowany i dodany do zmiennej środowiskowej PATH. Instrukcje instalacji FFmpeg można znaleźć [tutaj](https://www.wikihow.com/Install-FFmpeg-on-Windows).
- Pliki wykonywalne (exe): Niektóre części kodu korzystają z zewnętrznych aplikacji na Windowsie, które są dostarczane jako pliki exe. Te pliki muszą być dostępne w ścieżce systemowej lub w określonym miejscu, które jest zdefiniowane w ustawieniach programu.
- Znajomość obsługi terminala: Ponieważ program jest aplikacją terminalową, użytkownik musi być zaznajomiony z podstawowymi operacjami terminala.
- Zarządzanie ustawieniami: Większość ustawień programu jest automatycznie zapisywana w odpowiednim pliku JSON.

Proszę zauważyć, że niektóre funkcje programu mogą wymagać dodatkowych zależności, które są określone w pliku `requirements.txt`.

## ⚡ Instalacja

Aby zainstalować i skonfigurować **MM_AVH Working Space**, wykonaj następujące kroki:

1. **Pobierz skompresowany program**: Pobierz skompresowaną paczkę `mm_avh_working_space.zip`:

- Bezpośrednio z [Hugging Face](https://huggingface.co/datasets/MattyMroz/mm_avh_working_space/tree/main) (wykrywa jako niebezpieczny, bo zawiera pliki exe, które nie spełniają norm bezpieczeństwa \*\_\*)

2. **Rozpakuj pliki**: Rozpakuj pobrane pliki do wybranej lokalizacji.

3. **Przejdź do katalogu projektu**: Przejdź do głównego katalogu projektu mm_avh_working_space Na przykład w CMD:
   `cd mm_avh_working_space`

4. **Instaluj zależności Pythona**: Zainstaluj zależności Pythona z pliku `requirements.txt` za pomocą polecenia `pip install -r requirements.txt`.

5. **Poprawa jakości audio dla edge-tts**: Aby poprawić jakość audio dla edge-tts, wykonaj następujące kroki:

   - W Visual Studio Code (VSC) znajdź plik `modules/subtitle_to_speech.py`, najedź kursorem na `Communicate` i naciśnij `Ctrl + Click`, aby przejść do `communicate.py`.
   - Wyszukaj w pliku `communicate.py` `audio-24khz-48kbitrate-mono-mp3` i zamień na `audio-24khz-96kbitrate-mono-mp3`.

6. **Instalacja głosów systemowych**: Program korzysta z głosów systemowych dostarczanych przez Speech2Go i IVONA. Instalatory znajdują się w pliku `installation.zip`.

7. **Konfiguracja głosów API**: Program korzysta z edge-tts dla głosów API. Lista dostępnych głosów edge znajduje się pod tym [linkiem](https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4) lub w folderze `tests/tts_online_edge_test_1.py`. Istnieje również możliwość korzystania z Google TTS, ale jakość dźwięku może nie być zadowalająca dla długotrwałego słuchania.

8. **Konfiguracja głosów Eleven Labs**: Program może również korzystać z głosów dostarczanych przez Eleven Labs. Nie jest wymagana żadna dodatkowa instalacja lokalnie, ale musisz skierować się do odpowiedniego repozytorium GitHub z notatnikiem Google Colab i instrukcjami obsługi. Repozytorium znajdziesz pod adresem: [11Labs_TTS_Colab_Shere](https://github.com/MattyMroz/11Labs_TTS_Colab_Shere). PS.: Możliwe jest również korzystanie z głosów Eleven Labs za pomocą API, lokalnie, ale ta funkcja nie jest jeszcze zaimplementowana, ze względu na koszty API..., poprzednie rozwiązanie jest darmowe.

Po wykonaniu powyższych kroków, **MM_AVH Working Space** powinien być gotowy do użycia!

## 🔄 Aktualizacje

Główne aktualizacje będą wykonywane przeze mnie. Możesz pobrać najnowszą wersję za pomocą poniższego linku, tak samo jak w przypadku pierwszej instalacji.

[![Pobierz najnowszą wersję MM_AVH Working Space](https://img.shields.io/badge/Pobierz-najnowszą%20wersję%20MM_AVH%20Working%20Space-blue?style=for-the-badge&logo=github)](https://huggingface.co/datasets/MattyMroz/mm_avh_working_space/tree/main)

## 📝 Opis Programów

**MM_AVH Working Space** to zestaw narzędzi do przetwarzania plików multimedialnych, szczególnie plików MKV. Oto, co robi:

1. Ekstrahuje różne ścieżki (audio i napisy) z plików MKV w celu ich segregacji i przetworzenia.

2. Dzieli napisy w formacie ASS na podstawie poszczególnych stylów zawartych w pliku, a następnie konwertuje je na format SRT, gdzie później mogą być przetłumaczone.

3. Może zamienić liczby w napisach na liczebniki, co może być potencjalnie niegramatyczne, ale jest użyteczne w niektórych kontekstach.

4. Generuje audio na podstawie ustawień zawartych w pliku `settings.json`. Po wygenerowaniu audio, lektor jest łączony z audio.

5. Łączy wszystko w jeden plik MKV z napisami pobocznymi + lektorem lub z wypalonymi napisami.

6. Działa jako generator audiobooków. Wystarczy przekazać plik TXT lub SRT do folderu `working_space/temp`. Uwaga: plik po generacji zostanie usunięty.

Dzięki tym funkcjom, **MM_AVH Working Space** jest potężnym narzędziem do przetwarzania i tworzenia plików multimedialnych, szczególnie dla osób pracujących z plikami MKV i audiobookami.

## 📸 Demonstracja

<img src="./assets/img/mm_avh_working_space.gif" alt="" width="100%" height="">

## 📌 Uwagi

Chociaż **MM_AVH Working Space** został stworzony z myślą o ułatwieniu przetwarzania plików multimedialnych, pamiętaj, że korzystasz z tego zestawu narzędzi na własne ryzyko.

Podczas korzystania z **MM_AVH Working Space**, zawsze upewnij się, że masz kopie zapasowe swoich danych. Nie ponoszę odpowiedzialności za utratę danych lub uszczerbek na mieniu, który może wyniknąć z użycia tego zestawu narzędzi.

Pamiętaj, że jesteś odpowiedzialny za przestrzeganie wszelkich praw autorskich i innych praw własności intelektualnej podczas korzystania z **MM_AVH Working Space**.

<!-- - [🙏 Podziękowania](#-podziękowania) -->
<!-- ## 🙏 Podziękowania

Tutaj możesz podziękować osobom, które pomogły Ci w projekcie. Możesz podać ich imiona, role, jak pomogli. -->

## 📄 Licencja

Ten projekt jest licencjonowany na podstawie licencji zawartej w pliku [LICENCE](./LICENCE) dostępnym w tym samym folderze co ten plik README.

Zachęcam do zapoznania się z pełnym tekstem licencji, aby zrozumieć, jakie prawa i obowiązki wynikają z korzystania z **MM_AVH Working Space**.

## 📧 Kontakt

Jeśli masz jakiekolwiek pytania, sugestie lub chcesz skontaktować się ze mną w innej sprawie, możesz wysłać mi e-mail:

[![Wyślij e-mail](https://img.shields.io/badge/Email-mateuszmroz001%40gmail.com-blue?style=for-the-badge&logo=gmail)](mailto:mateuszmroz001@gmail.com)

Czekam na Twoją wiadomość!

<!-- Instalation:
git clone https://github.com/MattyMroz/mm_avh_working_space.git
cd mm_avh
pip install -r requirements.txt -->
