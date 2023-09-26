# # LEPSZA JAKOŚĆ
# # -> W VSC najedź kursorem na Communicate i naciśnij Ctrl + Click, aby przejść do communicate.py
# # -> Wyszukaj w pliku communicate.py audio-24khz-48kbitrate-mono-mp3 i zamień na audio-24khz-96kbitrate-mono-mp3

# pip install pyttsx3
# pip install pysrt
# pip install wave
# pip install asyncio
# pip install edge_tts
# pip install termcolor

import os
import time
import pysrt
import pyttsx3
import wave
import asyncio
import edge_tts
from termcolor import cprint
from pydub import AudioSegment
import nltk
import subprocess
import contextlib
import winsound


def tts_local(choice):
    def convert_srt_to_wav(dir_path):
        # Inicjalizacja silnika mowy
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if voice.name == 'Vocalizer Expressive Zosia Harpo 22kHz':
                engine.setProperty('voice', voice.id)
            engine.setProperty('rate', 200)  # Szybkość mówienia
            engine.setProperty('volume', 0.7)  # Głośność

        # Konwersja wszystkich plików srt w katalogu
        for file in os.listdir(dir_path):
            if file.endswith(".srt"):
                # Pobranie plików .srt
                subtitles = pysrt.open(os.path.join(
                    dir_path, file), encoding='ANSI')

                # Odczytanie napisów i zapisanie mowy do pliku WAV
                output_file = os.path.splitext(file)[0] + ".wav"
                with wave.open(output_file, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(22500)  # 22kHz

                    cprint('\n' + subtitles.path + '\n', 'green')
                    for i, subtitle in enumerate(subtitles, start=1):
                        print(
                            f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")

                        start_time = subtitle.start.to_time()
                        start_time = start_time.hour * 3600 + start_time.minute * \
                            60 + start_time.second + start_time.microsecond / 1000000
                        # Zapisanie mowy do pliku WAV
                        engine.save_to_file(subtitle.text, "temp.wav")
                        engine.runAndWait()

                        # Dodanie pustego frame'a do pliku WAV, jeśli jest to wymagane
                        framerate = wav_file.getframerate()
                        nframes = wav_file.getnframes()
                        current_time = nframes / float(framerate)
                        if start_time > current_time:
                            empty_frame_duration = int(
                                (start_time - current_time) * framerate)
                            empty_frame = b'\x00' * empty_frame_duration * 2
                            wav_file.writeframes(empty_frame)

                        # Dodanie mowy do pliku WAV
                        with wave.open("temp.wav", 'rb') as temp_file:
                            data = temp_file.readframes(temp_file.getnframes())
                            wav_file.writeframes(data)

                # Usunięcie pliku tymczasowego
                if os.path.exists("temp.wav"):
                    os.remove("temp.wav")

    def convert_srt_to_wav_balabolka(dir_path):
        # BALABOLKA - BALKON.EXE
        for file in os.listdir(dir_path):
            if file.endswith(".srt"):
                file_path = os.path.join(dir_path, file)
                with contextlib.suppress(UnicodeDecodeError):
                    subtitles = pysrt.open(file_path, encoding='ANSI')
                    cprint('\n' + subtitles.path + '\n', 'green')
                    for i, subtitle in enumerate(subtitles, start=1):
                        print(
                            f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")
                    command = f'balcon -f {file} -w {os.path.splitext(file)[0]}.wav -n "IVONA 2 Agnieszka" -s 5 -v 70'
                    subprocess.call(command, shell=True)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if choice == 1:
        convert_srt_to_wav(dir_path)

    if choice == 2:
        convert_srt_to_wav_balabolka(dir_path)


def tts_edge_online(choice):
    async def generate_speech(subtitle, voice, output_file, rate, volume):
        communicate = edge_tts.Communicate(
            subtitle.text, voice, rate=rate, volume=volume)
        await communicate.save(output_file)

    async def generate_wav_files(subtitles, voice, rate, volume):
        tasks = []
        mp3_files = []
        file_name = os.path.splitext(subtitles.path)[0]
        for i, subtitle in enumerate(subtitles, start=1):
            output_file = f"{file_name}_{i}.mp3"
            mp3_files.append(output_file)
            tasks.append(asyncio.create_task(generate_speech(
                subtitle, voice, output_file, rate, volume)))
            if i % 50 == 0:
                await asyncio.gather(*tasks)
                tasks = []
                # Poczekaj 5 sekund przed kontynuacją generowania plików
                time.sleep(2)
        await asyncio.gather(*tasks)
        return mp3_files

    def merge_audio_files(mp3_files, subtitles):
        file_name = os.path.splitext(subtitles.path)[0]
        with wave.open(f"{file_name}.wav", 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)

            audio_segments = []
            cprint('\n' + subtitles.path + '\n', 'green')
            for i, mp3_file in enumerate(mp3_files, start=1):
                print(
                    f"{i}\n{subtitles[i-1].start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitles[i-1].end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitles[i-1].text}\n")

                mp3_file_path = os.path.join(dir_path, mp3_file)
                if os.path.isfile(mp3_file_path):
                    start_time = subtitles[i-1].start.to_time()
                    start_time = start_time.hour * 3600 + start_time.minute * \
                        60 + start_time.second + start_time.microsecond / 1000000
                    sound = AudioSegment.from_file(
                        mp3_file_path, format="mp3")
                    audio_segments.append(sound)
                    os.remove(mp3_file_path)

                    framerate = wav_file.getframerate()
                    nframes = wav_file.getnframes()
                    current_time = nframes / float(framerate)
                    if current_time < start_time:
                        empty_frame_duration = int(
                            (start_time - current_time) * framerate)
                        empty_frame = b'\x00' * empty_frame_duration * 2
                        wav_file.writeframes(empty_frame)

                    sound_data = sound.raw_data
                    wav_file.writeframes(sound_data)

            wav_file.close()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir(dir_path):
        # Zmienne silnika mowy Edge TTS
        if choice == 3:
            VOICE = "pl-PL-ZofiaNeural"
        if choice == 4:
            VOICE = "pl-PL-MarekNeural"
        RATE = "+40%"
        VOLUME = "+0%"
        # RATE = "+0%"
        # VOLUME = "+0%"
        if file.endswith(".srt"):
            subtitles = pysrt.open(os.path.join(
                dir_path, file), encoding='ANSI')
            mp3_files = asyncio.run(generate_wav_files(
                subtitles, VOICE, RATE, VOLUME))
            merge_audio_files(mp3_files, subtitles)


def text_to_subtitles():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def clean_text(file_path):
        with open(file_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
        with open(file_path, 'w', encoding='utf8') as f:
            for line in lines:
                line = line.strip()
                f.write(line + "\n")

    def erasing_words(file_path):
        words = ["(", ")", "[", "]", "<", ">", "{", "}", "\"", "『", "』",
                 "…", "「", "」", "„", "”", "«", "»", "...", "*", "'", "〈", "〉", ""]
        with open(file_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
        with open(file_path, 'w', encoding='utf8') as f:
            for line in lines:
                for word in words:
                    line = line.replace(word, "")
                f.write(line)

    def txt_to_srt(file_path):
        print("txt to srt")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        text = text.split("\n")
        text = [x for x in text if x != ""]
        print(text)
        subs = pysrt.SubRipFile()
        index = 1
        for line in text:
            sentences = nltk.sent_tokenize(line)
            for sentence in sentences:
                if all(c in '.,?!:;-–—' for c in sentence):
                    continue
                subs.append(pysrt.SubRipItem(index, start='00:00:00,000',
                            end='00:00:00,000', text=sentence))
                index += 1
        srt_filename = os.path.splitext(file_path)[0] + "_.srt"
        subs.save(srt_filename, encoding='utf-8')

    for file in os.listdir(dir_path):
        if file.endswith(".txt"):
            file_path = os.path.join(dir_path, file)
            clean_text(file_path)
            erasing_words(file_path)
            txt_to_srt(file_path)

    for file_name in os.listdir(dir_path):
        if file_name.endswith(".srt"):
            file_path = os.path.join(dir_path, file_name)

            with contextlib.suppress(UnicodeDecodeError):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                with open(file_path, "w", encoding="ANSI") as file:
                    file.write(content)


def main():
    start_time = time.time()
    # red green yellow white attrs=['bold']
    cprint("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝",
           'white', attrs=['bold'])
    cprint("")
    cprint("Wybierz jedną z poniższych opcji (tylko .txt, .srt):")
    cprint("1. TTS - Zosia - Harpo")
    cprint("2. TTS - Agnieszka - Ivona")
    cprint("3. TTS - Zofia - Edge")
    cprint("4. TTS - Marek - Edge")

    choice = input("Wybierz numer opcji: ")
    text_to_subtitles()
    if choice == '1':
        tts_local(choice=1)
    if choice == '2':
        tts_local(choice=2)
    if choice == '3':
        tts_edge_online(choice=3)
    if choice == '4':
        tts_edge_online(choice=4)

        # Mierz czas
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %s minutes ---" % ((time.time() - start_time) / 60))
    print("--- %s hours ---" % ((time.time() - start_time) / 3600))

    winsound.PlaySound('complete.wav', winsound.SND_FILENAME)


if __name__ == "__main__":
    main()
