# pip install edge-tts
# https://github.com/rany2/edge-tts

# LEPSZA JAKOŚĆ!!!
# -> W VSC najedź kursorem na Communicate i naciśnij Ctrl + Click, aby przejść do communicate.py
# -> Wyszukaj w pliku communicate.py audio-24khz-48kbitrate-mono-mp3 i zamień na audio-24khz-96kbitrate-mono-mp3

"""
Podstawowe użycie edge-tts
"""
# CMD:
# edge-tts --text "Witaj świecie! Jak się masz? Mam nadzieję, że dobrze." --voice "pl-PL-ZofiaNeural" --rate "+100%" --volume "+0%" --write-media test.mp3

import asyncio
import os
import wave
from pydub import AudioSegment
import edge_tts
import pysrt

# VOICE = "pl-PL-ZofiaNeural"
VOICE = "pl-PL-MarekNeural"
RATE = "+50%"
VOLUME = "+0%"


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
    await asyncio.gather(*tasks)
    return mp3_files


def merge_audio_files(mp3_files, subtitles):
    file_name = os.path.splitext(subtitles.path)[0]
    with wave.open(f"{file_name}.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)

        audio_segments = []
        print('\n'+subtitles.path+'\n')
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


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir(dir_path):
        if file.endswith(".srt"):
            subtitles = pysrt.open(os.path.join(dir_path, file))
            mp3_files = asyncio.run(generate_wav_files(
                subtitles, VOICE, RATE, VOLUME))
            merge_audio_files(mp3_files, subtitles)


# DROGA :(
# import wave
# import pysrt
# import os
# from pydub import AudioSegment
# import subprocess

# VOICE = "pl-PL-ZofiaNeural"
# RATE = "+50%"

# # Konwersja wszystkich plików srt w katalogu
# dir_path = os.path.dirname(os.path.realpath(__file__))
# for file in os.listdir(dir_path):
#     if file.endswith(".srt"):
#         # Pobranie plików .srt
#         subtitles = pysrt.open(os.path.join(dir_path, file))

#         # Odczytanie napisów i zapisanie mowy do pliku WAV
#         output_file = os.path.splitext(file)[0] + ".wav"
#         with wave.open(output_file, 'wb') as wav_file:
#             wav_file.setnchannels(1)  # Mono
#             wav_file.setsampwidth(2)  # 16-bit
#             wav_file.setframerate(22500)  # 22kHz

#             for i, subtitle in enumerate(subtitles, start=1):
#                 print(
#                     f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")

#                 start_time = subtitle.start.to_time()
#                 start_time = start_time.hour * 3600 + start_time.minute * \
#                     60 + start_time.second + start_time.microsecond / 1000000

#                 # subprocess.call('edge-tts --text "' + subtitle.text +
#                 #                 '" --voice "pl-PL-MarekNeural" --rate "+50%" --write-media temp.mp3')
#                 subprocess.call('edge-tts --text "' + subtitle.text +
#                                 '" --voice "pl-PL-ZofiaNeural" --rate "+0%" --write-media temp.mp3')
#                 # Zapisanie mowy do pliku WAV
#                 sound = AudioSegment.from_file(
#                     "temp.mp3", format="mp3")
#                 sound.export("temp.wav", format="wav", parameters=[
#                              "-ac", "1", "-sample_fmt", "s16", "-ar", "22500"])

#                 # Dodanie pustego frame'a do pliku WAV, jeśli jest to wymagane
#                 framerate = wav_file.getframerate()
#                 nframes = wav_file.getnframes()
#                 current_time = nframes / float(framerate)
#                 if start_time > current_time:
#                     empty_frame_duration = int(
#                         (start_time - current_time) * framerate)
#                     empty_frame = b'\x00' * empty_frame_duration * 2
#                     wav_file.writeframes(empty_frame)

#                 # Dodanie mowy do pliku WAV
#                 with wave.open("temp.wav", 'rb') as temp_file:
#                     data = temp_file.readframes(temp_file.getnframes())
#                     wav_file.writeframes(data)

#         # Usunięcie pliku tymczasowego
#         os.remove("temp.mp3")
#         os.remove("temp.wav")


# 2.0

# pip install edge-tts
# https://github.com/rany2/edge-tts

# import wave
# import pysrt
# import os
# from pydub import AudioSegment
# import subprocess
# import edge_tts
# import asyncio

# VOICE = "pl-PL-ZofiaNeural"
# OUTPUT_FILE = "temp.mp3"
# OUTPUT_FILE_WAV = "temp.wav"
# RATE = "+50%"
# VOLUME = "+0%"


# async def _edge_tts(subtitle) -> None:
#     communicate = edge_tts.Communicate(
#         subtitle.text, VOICE, rate=RATE, volume=VOLUME)
#     await communicate.save(OUTPUT_FILE)


# async def main():
#     # Konwersja wszystkich plików srt w katalogu
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     for file in os.listdir(dir_path):
#         if file.endswith(".srt"):
#             # Pobranie plików .srt
#             subtitles = pysrt.open(os.path.join(dir_path, file))

#             # Odczytanie napisów i zapisanie mowy do pliku WAV
#             output_file = os.path.splitext(file)[0] + ".wav"
#             with wave.open(output_file, 'wb') as wav_file:
#                 wav_file.setnchannels(1)  # Mono
#                 wav_file.setsampwidth(2)  # 16-bit
#                 wav_file.setframerate(22500)  # 22kHz

#                 for i, subtitle in enumerate(subtitles, start=1):
#                     print(
#                         f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")

#                     start_time = subtitle.start.to_time()
#                     start_time = start_time.hour * 3600 + start_time.minute * \
#                         60 + start_time.second + start_time.microsecond / 1000000

#                     await _edge_tts(subtitle)

#                     sound = AudioSegment.from_file(
#                         OUTPUT_FILE, format="mp3")
#                     sound.export(OUTPUT_FILE_WAV, format="wav", parameters=[
#                                 "-ac", "1", "-sample_fmt", "s16", "-ar", "22500"])

#                     # Dodanie pustego frame'a do pliku WAV, jeśli jest to wymagane
#                     framerate = wav_file.getframerate()
#                     nframes = wav_file.getnframes()
#                     current_time = nframes / float(framerate)
#                     if start_time > current_time:
#                         empty_frame_duration = int(
#                             (start_time - current_time) * framerate)
#                         empty_frame = b'\x00' * empty_frame_duration * 2
#                         wav_file.writeframes(empty_frame)

#                     # Dodanie mowy do pliku WAV
#                     with wave.open(OUTPUT_FILE_WAV, 'rb') as temp_file:
#                         data = temp_file.readframes(temp_file.getnframes())
#                         wav_file.writeframes(data)

#             # Usunięcie pliku tymczasowego
#             os.remove(OUTPUT_FILE)
#             os.remove(OUTPUT_FILE_WAV)


# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import os
# from pydub import AudioSegment
# import edge_tts
# import subprocess
# import pysrt


# VOICE = "pl-PL-ZofiaNeural"
# RATE = "+50%"
# VOLUME = "+0%"


# async def generate_speech(subtitle, voice, output_file, rate, volume):
#     communicate = edge_tts.Communicate(subtitle.text, voice, rate=rate, volume=volume)
#     await communicate.save(output_file)


# async def generate_wav_files(subtitles, voice, rate, volume):
#     tasks = []
#     file_name = os.path.splitext(subtitles.path)[0]
#     for i, subtitle in enumerate(subtitles, start=1):
#         output_file = f"{file_name}_{i}.mp3"
#         tasks.append(asyncio.create_task(generate_speech(subtitle, voice, output_file, rate, volume)))
#     await asyncio.gather(*tasks)


# if __name__ == "__main__":
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     for file in os.listdir(dir_path):
#         if file.endswith(".srt"):
#             subtitles = pysrt.open(os.path.join(dir_path, file))
#             asyncio.run(generate_wav_files(subtitles, VOICE, RATE, VOLUME))

#     # Przejście przez wszystkie pliki w bieżącym katalogu
#     for file in os.listdir('.'):
#         if file.endswith('.mp3'):
#             mp3_file = AudioSegment.from_mp3(file)

#             # Zapis pliku WAV
#             wav_file = file.replace('.mp3', '.wav')
#             mp3_file.export(wav_file, format='wav')

#             # Usunięcie pliku MP3
#             os.remove(file)

# 4.
# import asyncio
# import os
# import wave
# from pydub import AudioSegment
# import edge_tts
# import subprocess
# import pysrt

# VOICE = "pl-PL-ZofiaNeural"
# RATE = "+50%"
# VOLUME = "+0%"


# async def generate_speech(subtitle, voice, output_file, rate, volume):
#     communicate = edge_tts.Communicate(subtitle.text, voice, rate=rate, volume=volume)
#     await communicate.save(output_file)


# async def generate_wav_files(subtitles, voice, rate, volume):
#     tasks = []
#     file_name = os.path.splitext(subtitles.path)[0]
#     for i, subtitle in enumerate(subtitles, start=1):
#         output_file = f"{file_name}_{i}.mp3"
#         tasks.append(asyncio.create_task(generate_speech(subtitle, voice, output_file, rate, volume)))
#     await asyncio.gather(*tasks)


# if __name__ == "__main__":
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     for file in os.listdir(dir_path):
#         if file.endswith(".srt"):
#             subtitles = pysrt.open(os.path.join(dir_path, file))
#             asyncio.run(generate_wav_files(subtitles, VOICE, RATE, VOLUME))

#     # Przejście przez wszystkie pliki w bieżącym katalogu
#     for file in os.listdir('.'):
#         if file.endswith('.mp3'):
#             mp3_file = AudioSegment.from_mp3(file)

#             # Zapis pliku WAV
#             wav_file = file.replace('.mp3', '.wav')
#             mp3_file.export(wav_file, format='wav')

#             # Usunięcie pliku MP3
#             os.remove(file)

#             # Przetwarzanie pliku WAV
#             with wave.open(wav_file, 'rb') as input_file:
#                 output_file = os.path.splitext(file)[0] + ".wav"
#                 with wave.open(output_file, 'wb') as wav_file:
#                     wav_file.setnchannels(1)  # Mono
#                     wav_file.setsampwidth(2)  # 16-bit
#                     wav_file.setframerate(22500)  # 22kHz

#                     for i, subtitle in enumerate(subtitles, start=1):
#                         print(
#                             f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")

#                         start_time = subtitle.start.to_time()
#                         start_time = start_time.hour * 3600 + start_time.minute * \
#                             60 + start_time.second + start_time.microsecond / 1000000

#                         # Dodanie pustego frame'a do pliku WAV, jeśli jest to wymagane
#                         framerate = wav_file.getframerate()
#                         nframes = wav_file.getnframes()
#                         current_time = nframes / float(framerate)
#                         if start_time > current_time:
#                             empty_frame_duration = int(
#                                 (start_time - current_time) * framerate)
#                             empty_frame = b'\x00' * empty_frame_duration * 2
#                             wav_file.writeframes(empty_frame)

#                         # Dodanie mowy do pliku WAV
#                         with wave.open(output_file, 'rb') as temp_file:
#                             data = temp_file.readframes(temp_file.getnframes())
#                             wav_file.writeframes(data)

#             # Usunięcie pliku tymczasowego
#             os.remove(output_file)


# import asyncio
# import os
# import wave
# from pydub import AudioSegment
# import edge_tts
# import subprocess
# import pysrt

# VOICE = "pl-PL-ZofiaNeural"
# RATE = "+50%"
# VOLUME = "+0%"


# async def generate_speech(subtitle, voice, output_file, rate, volume):
#     communicate = edge_tts.Communicate(
#         subtitle.text, voice, rate=rate, volume=volume)
#     await communicate.save(output_file)
#     return output_file


# async def generate_wav_files(subtitles, voice, rate, volume):
#     tasks = []
#     mp3_files = []
#     file_name = os.path.splitext(subtitles.path)[0]
#     for i, subtitle in enumerate(subtitles, start=1):
#         output_file = f"{file_name}_{i}.mp3"
#         mp3_files.append(output_file)
#         tasks.append(asyncio.create_task(generate_speech(
#             subtitle, voice, output_file, rate, volume)))
#     await asyncio.gather(*tasks)
#     return mp3_files


# if __name__ == "__main__":
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     for file in os.listdir(dir_path):
#         if file.endswith(".srt"):
#             subtitles = pysrt.open(os.path.join(dir_path, file))
#             mp3_files = asyncio.run(generate_wav_files(
#                 subtitles, VOICE, RATE, VOLUME))
#             for mp3_file in mp3_files:
#                 mp3_file_path = os.path.join(dir_path, mp3_file)
#                 if os.path.isfile(mp3_file_path):
#                     mp3_file_basename = os.path.splitext(mp3_file)[0]
#                     wav_file = f"{mp3_file_basename}.wav"
#                     mp3_audio = AudioSegment.from_file(
#                         mp3_file_path, format="mp3")
#                     mp3_audio.export(wav_file, format="wav")
#                     os.remove(mp3_file_path)


#             # for i, subtitle in enumerate(subtitles, start=1):
#             #     print(
#             #         f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")
#             #     start_time = subtitle.start.to_time()
#             #     start_time = start_time.hour * 3600 + start_time.minute * \
#             #         60 + start_time.second + start_time.microsecond / 1000000
#             #     # 1.srt
#             #     # 10
#             #     # = 1_10.wav
#             #     # wavfile = file[:-4] + "_" + str(i) + ".wav"
#             #     # print(file)
#             #     # print(i)
