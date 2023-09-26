# balcon -f 1.srt -w 1.wav -n "IVONA 2 Agnieszka" --sub-fit --sub-max 2
# pip install warnings


import contextlib
import os
import subprocess

dir_path = os.path.dirname(os.path.realpath(__file__))

for file_name in os.listdir(dir_path):
    if file_name.endswith(".srt"):
        file_path = os.path.join(dir_path, file_name)

        with contextlib.suppress(UnicodeDecodeError):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            with open(file_path, "w", encoding="ansi") as file:
                file.write(content)

command = """balcon -f 1.srt -w 1.wav -n "Microsoft Paulina Desktop" -s 7 -v 70"""
subprocess.call(command, shell=True)
subprocess.call('balcon -l -n "IVONA 2 Agnieszka" -m', shell=True)
# subprocess.call("balcon -g", shell=True)


# -l : drukowanie listy głosów
# -g : wyświetla listę urządzeń wyjściowych audio
# -f <nazwa_pliku> : ustawia wejściowy plik tekstowy
# -fl <nazwa_pliku> : ustawia plik z listą nazw plików wejściowych
# -w <nazwa_pliku> : ustawia plik wyjściowy w formacie WAV
# -n <nazwa_głosu> : ustaw głos dla mowy
# -id <liczba całkowita> : ustawia głos według kodu języka (Locale ID)
# -m : drukuj parametry głosu
# -b <liczba całkowita> : ustawienie urządzenia wyjściowego audio według indeksu
# -r <tekst> : ustawienie urządzenia wyjściowego audio według nazwy
# -c : użyj tekstu ze schowka
# -t <tekst> : użyj tekstu z wiersza poleceń
# -i : użyj tekstu ze stdin
# -o : zapis danych dźwiękowych na stdout
# -s <liczba całkowita> : ustaw szybkość mowy (od -10 do 10)
# -p <liczba całkowita> : ustawienie wysokości dźwięku (od -10 do 10)
# -v <liczba całkowita> : ustawienie głośności mowy (od 0 do 100)
# -e <liczba całkowita> : pauza między zdaniami (w milisekundach)
# -a <liczba całkowita> : pauza między akapitami (w milisekundach)
# -d <nazwa_pliku> : zastosuj słownik do korekty wymowy
# -k : zabija inne kopie aplikacji
# -ka : zabija aktywną kopię aplikacji
# -pr : wstrzymanie lub wznowienie czytania przez aktywną kopię aplikacji
# -q : dodaj aplikację do kolejki
# -lrc : tworzy plik LRC do wyświetlania zsynchronizowanego tekstu w odtwarzaczach audio
# -srt : tworzy plik SRT do wyświetlania zsynchronizowanego tekstu w odtwarzaczach wideo
# -vs <nazwa_pliku> : tworzy plik tekstowy ze zsynchronizowanymi wizualizacjami
# -sub : przetwarza tekst wejściowy jako napisy
# -tray : wyświetla ikonę w zasobniku systemowym
# -ln <liczba całkowita> : wybierz linię według numeru (lub zakresu, np. 12-79)
# -fr <liczba całkowita> : ustaw wyjściową częstotliwość próbkowania dźwięku w kHz (od 8 do 48)
# -bt <liczba całkowita> : ustawienie wyjściowej głębi bitowej audio (8 lub 16)
# -ch <liczba całkowita> : ustawienie trybu wyjściowego kanału audio (1 lub 2)
# -enc <kodowanie> : ustaw kodowanie tekstu wejściowego (ansi, utf8 lub unicode)
# -sb <liczba całkowita> : cisza na początku (w milisekundach)
# -se <liczba całkowita> : cisza na końcu (w milisekundach)
# -df : usuwa plik tekstowy po zakończeniu zadania
# -isb : ignoruje tekst w nawiasach kwadratowych
# -icb : ignoruje tekst w nawiasach klamrowych
# -iab : ignoruje tekst w nawiasach kątowych
# -irb : ignoruje tekst w nawiasach okrągłych
# -iu : ignoruje adresy URL
# -ic : ignoruje /*komentarze*/ w tekście
# -h : drukuje informacje o użyciu

# --lrc-length <liczba całkowita> : ustawia maksymalną długość linii tekstu dla wyjściowego pliku LRC
# --lrc-fname <nazwa_pliku> : ustawia nazwę pliku dla wyjściowego pliku LRC
# --lrc-enc <kodowanie> : ustaw kodowanie dla wyjściowego pliku LRC
# --lrc-offset <liczba całkowita> : ustawia przesunięcie czasowe dla wyjściowego pliku LRC (w milisekundach)
# --lrc-artist <text> : artysta (znacznik ID)
# --lrc-album <tekst> : album (znacznik ID)
# --lrc-title <text> : tytuł (znacznik ID)
# --lrc-author <text> : autor (znacznik ID)
# --lrc-creator <text> : twórca pliku LRC (znacznik ID)
# --lrc-sent : wstaw puste linie po zdaniach w pliku LRC
# --lrc-para : wstawia puste linie po akapitach w pliku LRC
# --srt-length <liczba całkowita> : ustawia maksymalną długość linii tekstu dla wyjściowego pliku SRT
# --srt-fname <nazwa_pliku> : ustaw nazwę pliku dla wyjściowego pliku SRT
# --srt-enc <kodowanie> : ustaw kodowanie dla wyjściowego pliku SRT
# --raw : wyjście to surowe dane PCM (bez nagłówka)
# --ignore-length : pomija długość danych audio w nagłówku WAV
# --sub-format <text> : ustaw format napisów (dla tekstu wejściowego)
# --sub-max <liczba całkowita> : ustawia maksymalną szybkość mowy dla napisów

# --voice1-name <nazwa_głosu> : ustaw głos do czytania obcych słów w tekście
# --voice1-langid <language_id> : ustaw identyfikator języka dla obcego tekstu (np. en)
# --voice1-rate <integer> : ustaw szybkość mowy dla obcego tekstu (od -10 do 10)
# --voice1-pitch <integer> : ustawienie wysokości mowy dla obcego tekstu (od -10 do 10)
# --voice1-volume <integer> : ustaw głośność mowy dla obcego tekstu (od 0 do 100)
# --voice1-roman : użyj domyślnego głosu do czytania cyfr rzymskich
# --voice1-digit : użyj domyślnego głosu do odczytywania cyfr w obcym tekście
# --voice1-length <liczba całkowita> : ustaw minimalną długość obcego tekstu, aby zmienić głos
