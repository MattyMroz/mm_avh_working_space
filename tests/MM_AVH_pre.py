# Program: Multimedia Magic - Audio Visual Heaven (MM-AVH) do automatyzacji procesu tłumaczenia napisów i lektora do filmów

# pip install pysubs2
# pip install googletrans==3.1.0a0
import re
import threading
import shutil
import pyautogui
import pyperclip
import time
import deepl
import pysrt
from googletrans import Translator
from pysubs2 import SSAFile
from pysubs2 import SSAFile
from pyasstosrt import Subtitle
import subprocess
import os
from termcolor import cprint
import json
import contextlib
import asyncio
import wave
import edge_tts
import pyttsx3
from pydub import AudioSegment
import webbrowser
from revChatGPT.V1 import Chatbot


def execute_command(command):
    subprocess.call(command, shell=True)


def directory_path():
    return os.path.dirname(os.path.realpath(__file__))


def set_option(prompt, options, description=None):
    cprint(prompt, 'yellow', attrs=['bold'])
    for key, value in options.items():
        if description and key in description:
            print(f"Wartość domyślna: {value:5} {description[key]:5}")
        else:
            print(f"{key}. {value}")
    cprint("\nWpisz swój wybór lub poprawną wartość:",
           'green', attrs=['bold'], end=" ")
    return input()


def is_valid_speed(speed, voice_choice):
    if voice_choice == '1':  # TTS - Zosia - Harpo
        return int(speed) > 0
    elif voice_choice == '2':  # TTS - Agnieszka - Ivona
        return -10 <= int(speed) <= 10
    elif voice_choice in ['3', '4']:  # TTS - Zofia - Edge, TTS - Marek - Edge
        return speed.startswith(('+', '-')) and speed[1:-1].isdigit() and -100 <= int(speed[1:-1]) <= 100 and speed.endswith('%')
    return False


def is_valid_volume(volume, voice_choice):
    if voice_choice == '1':  # TTS - Zosia - Harpo
        return 0 <= float(volume) <= 1
    elif voice_choice == '2':  # TTS - Agnieszka - Ivona
        return -100 <= int(volume) <= 100
    elif voice_choice in ['3', '4']:  # TTS - Zofia - Edge, TTS - Marek - Edge
        return volume.startswith(('+', '-')) and volume[1:-1].isdigit() and -100 <= int(volume[1:-1]) <= 100 and volume.endswith('%')
    return False


def set_settings(dir_path, settings):
    translator_options = {
        '1': 'Google Translate',
        '2': 'DeepL API',
        '3': 'DeepL Desktop',
        '4': 'ChatGPT 3.5 Free'
    }

    translated_line_count_options = {
        '1': '30',
        '2': '50',
        '3': '75',
        '4': '100',
    }

    alt_main_translator_options = {
        '1': 'yes',
        '2': 'no'
    }

    tts_voice_options = {
        '1': {
            'name': 'TTS - Zosia - Harpo',
            'speed_default': '200',
            'volume_default': '0.7'
        },
        '2': {
            'name': 'TTS - Agnieszka - Ivona',
            'speed_default': '5',
            'volume_default': '65'
        },
        '3': {
            'name': 'TTS - Zofia - Edge',
            'speed_default': '+40%',
            'volume_default': '+0%'
        },
        '4': {
            'name': 'TTS - Marek - Edge',
            'speed_default': '+40%',
            'volume_default': '+0%'
        }
    }

    output_options = {
        '1': 'Oglądam w MM_AVH_Players',
        '2': 'Scal do mkv',
        '3': 'Wypal do mp4',
    }

    cprint("╔═════════════════ Ustawienia ═════════════════╗\n",
           'white', attrs=['bold'])
    translator_choice = set_option(
        "Wybierz translatora:", translator_options
    )

    deepl_api_key = ''
    cprint("\nCzy chcesz ustawić klucz API DeepL? (t / y = tak):",
           'yellow', attrs=['bold'], end=" ")
    change_settings = input("")
    if change_settings.lower() in ['t', 'y', 'tak', 'yes']:
        cprint('Wpisz klucz API DeepL:', 'green', attrs=['bold'], end=' ')
        deepl_api_key = input()
        if deepl_api_key == '':
            cprint("Pominięto.", 'red', attrs=['bold'])
            if settings['deepl_api_key']:
                deepl_api_key = settings['deepl_api_key']
    else:
        cprint("Pominięto.", 'red', attrs=['bold'])
        if settings['deepl_api_key']:
            deepl_api_key = settings['deepl_api_key']

    access_token = ''
    cprint("\nCzy chcesz ustawić token dostępu do ChatGPT? (t / y = tak):",
           'yellow', attrs=['bold'], end=" ")
    change_settings = input()
    if change_settings.lower() in ['t', 'y', 'tak', 'yes']:
        url = "https://chat.openai.com/api/auth/session"
        webbrowser.open(url)
        cprint('Wpisz token dostępu do ChatGPT:',
               'green', attrs=['bold'], end=' ')
        access_token = input()
        if access_token == '':
            cprint("Pominięto.", 'red', attrs=['bold'])
            if settings['access_token']:
                access_token = settings['access_token']
    else:
        cprint("Pominięto.", 'red', attrs=['bold'])
        if settings['access_token']:
            access_token = settings['access_token']

    translated_line_count_choice = set_option(
        "\nWybierz ilość tłumaczonych linii na raz:", translated_line_count_options
    )
    alt_main_translator_choice = set_option(
        "\nCzy tłumaczyć rozdzielone napisy?", alt_main_translator_options
    )
    tts_choice = None
    while tts_choice is None:
        tts_choice = set_option(
            "\nWybierz głos lektora:", tts_voice_options
        )
        if tts_choice not in tts_voice_options:
            tts_choice = '2'  # Ustawienie domyślnej wartości

    tts_speed_default = tts_voice_options.get(tts_choice).get('speed_default')

    cprint("\nObesługiwane zakresy szybkości:",
           'yellow', attrs=['bold'])
    print("TTS - Zosia - Harpo     - szybkość głosu od 0 do ... (słowa na minute), domyślna: 200)")
    print("TTS - Agnieszka - Ivona - szybkość głosu od -10 do 10 (domyślna: 5)")
    print("TTS - Zofia - Edge      - szybkość głosu (+/-) od -100% do +100%, (domyślna: +40%)")
    print("TTS - Marek - Edge      - szybkość głosu (+/-) od -100% do +100%, (domyślna: +40%)")

    cprint(f"\nWpisz szybkość głosu (domyślna: {tts_speed_default}):", 'green', attrs=[
           'bold'], end=" ")
    tts_speed_choice = input('')
    try:
        tts_speed = (
            tts_speed_choice if is_valid_speed(tts_speed_choice, tts_choice) and tts_speed_choice.strip() != ''
            else tts_speed_default
        )
    except Exception:
        tts_speed = tts_speed_default
    cprint("\nObesługiwane zakresy głośności:", 'yellow', attrs=['bold'])
    print("TTS - Zosia - Harpo     - głośność głosu od 0 do 1 (domyślna: 0.7)")
    print("TTS - Agnieszka - Ivona - głośność głosu od 0 do 100 (domyślna: 65)")
    print("TTS - Zofia - Edge      - głośność głosu (+/-) od -100% do +100%, (domyślna: +0%)")
    print("TTS - Marek - Edge      - głośność głosu (+/-) od -100% do +100%, (domyślna: +0%)")
    tts_volume_default = tts_voice_options.get(
        tts_choice).get('volume_default')
    cprint(f"\nWpisz głośność głosu (domyślna: {tts_volume_default}):", 'green', attrs=[
           'bold'], end=" ")
    tts_volume_choice = input('')
    try:
        tts_volume = (
            tts_volume_choice if is_valid_volume(tts_volume_choice, tts_choice) and tts_volume_choice.strip() != ''
            else tts_volume_default
        )
    except Exception:
        tts_volume = tts_volume_default

    output_options_choice = set_option(
        "\nWybierz sposób wyjścia:", output_options
    )

    settings_data = {
        'translator': translator_options.get(translator_choice, 'Google Translate'),
        # jeśli nie jest pusty 1df708bf-af10-3e70-e577-b2d4cb763d74:fx
        'deepl_api_key': deepl_api_key,
        'access_token': access_token,
        'translated_line_count': translated_line_count_options.get(translated_line_count_choice, '50'),
        'alt_main_translator': alt_main_translator_options.get(alt_main_translator_choice, 'no'),
        'tts': tts_voice_options.get(tts_choice).get('name', 'TTS - Agnieszka - Ivona'),
        'tts_speed': tts_speed,
        'tts_volume': tts_volume,
        'output': output_options.get(output_options_choice, 'Oglądam w MM_AVH_Players')
    }

    with open(os.path.join(dir_path, 'src', 'settings.json'), 'w') as settings_file:
        json.dump(settings_data, settings_file, indent=4)

    cprint("Ustawienia zostały zapisane.\n", 'green', attrs=['bold'])


def get_settings(dir_path):
    if os.path.isfile(os.path.join(dir_path, 'src', 'settings.json')):
        with open(os.path.join(dir_path, 'src', 'settings.json'), 'r') as settings_file:
            settings_data = json.load(settings_file)
        return settings_data


def mkv_info(dir_path, file):
    command = [
        dir_path + '\\src\\mkvtoolnix\\mkvmerge.exe',
        '--ui-language',
        'en',
        '--identify',
        '--identification-format',
        'json',
        dir_path + '\\' + file
    ]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = process.communicate()

    if process.returncode == 0:
        return mkv_info_print(output, file)
    else:
        print(f'Error: {error}')


def mkv_info_print(output, file):
    data = json.loads(output)
    tracks_data = []

    for track in data['tracks']:
        track_data = {
            'id': track['id'],
            'type': track['type'],
            'codec_id': track['properties']['codec_id'],
            'language': track['properties']['language'],
            'language_ietf': track['properties']['language_ietf'],
            'properties': None
        }

        if 'display_dimensions' in track['properties']:
            track_data['properties'] = track['properties']['display_dimensions']
        elif 'audio_sampling_frequency' in track['properties']:
            track_data['properties'] = f"{track['properties']['audio_sampling_frequency']} Hz"

        tracks_data.append(track_data)

    cprint('WYODRĘBNIANIE Z PLIKU:', 'red', attrs=['bold'])
    cprint(file, 'white', attrs=['bold'])
    cprint('ID  TYPE        CODEK                LANG  LANG_IETF  PROPERTIES',
           'yellow', attrs=['bold'])

    sorted_tracks = sorted(tracks_data, key=lambda x: x['id'])
    for track in sorted_tracks:
        print(f'{track["id"]:2}  {track["type"]:10}  {track["codec_id"]:20} {track["language"]:5} {track["language_ietf"]:10} {track["properties"]}')

    print('')
    return data


def mkv_extract(dir_path, file, data):
    tracks_properties = []
    while True:
        try:
            cprint('Podaj ID ścieżki do wyciągnięcia (naciśnij ENTER, aby zakończyć): ',
                   'green', attrs=['bold'], end='')
            track_id = int(
                input(''))
            tracks_properties.append(track_id)
        except ValueError:
            cprint('Pominięto wyciąganie ścieżki.\n', 'red', attrs=['bold'])
            break
    try:
        for track_id in tracks_properties:
            track = data['tracks'][track_id]
            codec_id = track["properties"]["codec_id"]
            filename = f'{file[:-4]}.{codec_id.rsplit("_", 1)[-1].rsplit("/", 1)[-1].lower()}'
            out_file = os.path.join(dir_path, 'src', 'tmp', filename)
            command = [
                os.path.join(dir_path, 'src', 'mkvtoolnix', 'mkvextract.exe'),
                'tracks',
                os.path.join(dir_path, file),
                f'{track_id}:{out_file}'
            ]
            process = subprocess.Popen(command)
            cprint(
                f'Ekstrakcja ścieżki {track_id} do pliku {filename}', 'green', attrs=['bold'])
            process.communicate()
            print('')
    except IndexError:
        cprint('Znaleziono nieprawidłowe ID ścieżki!', 'red', attrs=['bold'])
        mkv_extract(dir_path, file, data)
        print('')


def split_ass(dir_path, input_file):
    main_subs_folder = os.path.join(dir_path, 'main_subs')
    alt_subs_folder = os.path.join(dir_path, 'alt_subs')

    with open(os.path.join(dir_path, input_file), 'r', encoding='utf-8') as file:
        subs = SSAFile.from_file(file)

    # Znajdź unikalne style w kolejności występowania
    styles = []
    for event in subs:
        if event.style not in styles:
            styles.append(event.style)

    cprint("PODZIAŁ PLIKU: ", 'red', attrs=['bold'])
    cprint(input_file, 'white', attrs=['bold'])
    # Wyświetl dostępne style w kolejności występowania
    cprint("Dostępne style do TTS:", 'yellow', attrs=['bold'])
    for i, style in enumerate(styles, start=1):
        print(f"{i}. {style}")

    print('')
    selected_styles = []
    while True:
        cprint("Wybierz style do zapisu (naciśnij ENTER, aby zakończyć): ",
               'green', attrs=['bold'], end='')
        selection = input("")
        if not selection:
            break
        selected_styles.append(styles[int(selection) - 1])

    if not selected_styles:
        cprint("Nie wybrano żadnych stylów. Podział napisów nie został wykonany.\n",
               'red', attrs=['bold'])
        return

    main_subs = SSAFile()
    alt_subs = SSAFile()

    for event in subs:
        if event.style in selected_styles:
            main_subs.append(event)
        else:
            alt_subs.append(event)

    main_output_file = os.path.join(main_subs_folder, input_file)
    alt_output_file = os.path.join(alt_subs_folder, input_file)

    # Skopiuj metadane do plików wyjściowych
    main_subs.info = subs.info
    alt_subs.info = subs.info

    # Skopiuj style do plików wyjściowych
    main_style_names = [style_name for style_name in subs.styles.keys()
                        if style_name in selected_styles]
    main_subs.styles.clear()
    for style_name in main_style_names:
        main_subs.styles[style_name] = subs.styles[style_name]

    alt_style_names = [style_name for style_name in subs.styles.keys()
                       if style_name not in selected_styles]
    alt_subs.styles.clear()
    for style_name in alt_style_names:
        alt_subs.styles[style_name] = subs.styles[style_name]

    # Zapisz napisy w plikach wyjściowych
    with open(main_output_file, 'w', encoding='utf-8') as main_file:
        main_file.write(main_subs.to_string(format_='ass'))

    with open(alt_output_file, 'w', encoding='utf-8') as alt_file:
        alt_file.write(alt_subs.to_string(format_='ass'))

    cprint("Podział napisów został zakończony.", 'yellow', attrs=['bold'])

    os.remove(os.path.join(dir_path, input_file))
    cprint("Usunięto plik źródłowy.\n", 'yellow', attrs=['bold'])


def ass_to_srt(dir_path, file):
    sub = Subtitle(os.path.join(dir_path, file))
    sub.export()
    cprint("Zamieniono na srt:", 'yellow', attrs=['bold'], end=" ")
    print(file)

    # os.remove(os.path.join(dir_path, file))
    # cprint("Usunięto plik źródłowy.", 'green', attrs=['bold'])


def asnii_srt(dir_path, file):
    with open(os.path.join(dir_path, file), "r", encoding="utf-8") as source_file:
        content = source_file.read()

    try:
        with open(os.path.join(dir_path, file), "w", encoding="ANSI") as target_file:
            target_file.write(content)
    except UnicodeEncodeError:
        with open(os.path.join(dir_path, file), "w", encoding="ANSI", errors="ignore") as target_file:
            target_file.write(content)

    # Zamieniono kodowanie pliku na ANSI
    cprint("Zamieniono kodowanie na ANSI:", 'yellow', attrs=['bold'], end=' ')
    print(file)


def translate_google(dir_path, file, translated_line_count):
    subs = pysrt.open(os.path.join(dir_path, file), encoding='utf-8')
    subs_combined = []
    translated_subs = []

    translator = Translator()
    for i, sub in enumerate(subs):
        sub.text = sub.text.replace("\n", " ◍ ")
        subs_combined.append(sub.text)

        if (i + 1) % translated_line_count == 0 or i == len(subs) - 1:
            combined_text = "\n".join(subs_combined)
            translated_text = translator.translate(
                combined_text, dest='pl').text
            translated_subs += translated_text.split("\n")
            subs_combined = []

    for i, sub in enumerate(subs):
        sub.text = translated_subs[i]
        sub.text = sub.text.replace(" ◍, ", ",\n")
        sub.text = sub.text.replace(" ◍ ", "\n")
        sub.text = sub.text.replace(" ◍", "")

    subs.save(os.path.join(dir_path, file))


def translate_deepl_api(dir_path, file, translated_line_count, settings):
    subs = pysrt.open(os.path.join(dir_path, file), encoding='utf-8')
    # Zamień na swój klucz https://www.deepl.com/pl/pro-api?cta=header-pro-api/ za darmo 5000000 słów miesięcznie
    # auth_key = "1df708bf-af10-3e70-e577-b2d4cb763d74:fx"
    auth_key = settings['deepl_api_key']
    translator = deepl.Translator(auth_key)
    groups = [subs[i:i+translated_line_count]
              for i in range(0, len(subs), translated_line_count)]
    for group in groups:
        text = " @\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                           for sub in group)
        translated_text = translator.translate_text(
            text, target_lang='PL').text
        translated_texts = translated_text.split(" @\n")
        if len(translated_texts) == len(group):
            for i in range(len(group)):
                if i < len(translated_texts):
                    group[i].text = translated_texts[i]
                    group[i].text = group[i].text.replace(" ◍◍◍◍, ", ",\n")
                    group[i].text = group[i].text.replace(" ◍◍◍◍ ", "\n")
                    group[i].text = group[i].text.replace(" ◍◍◍◍", "")
    subs.save(os.path.join(dir_path, file), encoding='utf-8')


def translate_deepl_desktop(dir_path, file, translated_line_count):
    # subprocess.Popen(
    #     r"C:\Users\mateu\AppData\Roaming\0install.net\desktop-integration\stubs\90d46b1a865bf05507b9fb0d2b3698b63cba3a15fbcafd836ab5523e7a3efb99\DeepL.exe")
    # lub
    command = r'C:\Users\mateu\AppData\Roaming\Programs\Zero Install\0install-win.exe'
    args = ["run", "--no-wait",
            "https://appdownload.deepl.com/windows/0install/deepl.xml"]
    subprocess.call([command] + args)

    time.sleep(5)

    def auto_steps():
        screen_width, screen_height = pyautogui.size()
        x = screen_width * 0.25
        y = screen_height * 0.5
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('del')
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(6)
        x = screen_width * 0.75
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')

    subs = pysrt.open(os.path.join(dir_path, file), encoding='utf-8')
    groups = [subs[i:i+translated_line_count]
              for i in range(0, len(subs), translated_line_count)]

    for group in groups:
        text = " @\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                           for sub in group)
        text = text.rstrip('\n')
        pyperclip.copy(text)
        auto_steps()

        translated_text = pyperclip.paste()
        if translated_text:
            for sub, trans_text in zip(group, translated_text.split(" @\n")):
                sub.text = trans_text.replace(" ◍◍◍◍, ", ",\n")
                sub.text = sub.text.replace(" ◍◍◍◍ ", "\n")
                sub.text = sub.text.replace(" ◍◍◍◍", "")

    subs.save(os.path.join(dir_path, file), encoding='utf-8')

    frezes = ["\nPrzetłumaczono z www.DeepL.com/Translator (wersja darmowa)\n",
              "Przetłumaczono z www.DeepL.com/Translator (wersja darmowa)",
              "\nTranslated with www.DeepL.com/Translator (free version)\n",
              "\nTranslated with www.DeepL.com/Translator (free version)"]

    with open(os.path.join(dir_path, file), 'r', encoding='utf-8') as in_file:
        text = in_file.read()

    for freze in frezes:
        text = text.replace(freze, "")

    with open(os.path.join(dir_path, file), 'w', encoding='utf-8') as out_file:
        out_file.write(text)


def translate_chatgpt_free(dir_path, file, translated_line_count, settings):

    subs = pysrt.open(os.path.join(dir_path, file), encoding='utf-8')
    subs_combined = []
    translated_subs = []

    for i, sub in enumerate(subs):
        sub.text = sub.text.replace("\n", " ◍ ")
        subs_combined.append(sub.text)

        if (i + 1) % translated_line_count == 0 or i == len(subs) - 1:
            combined_text = "\n".join(subs_combined)
            translated_text = ask_chatgpt(combined_text, settings)
            translated_subs += translated_text.split("\n")
            subs_combined = []

    for i, sub in enumerate(subs):
        sub.text = translated_subs[i]
        sub.text = sub.text.replace(" ◍, ", ",\n")
        sub.text = sub.text.replace(" ◍ ", "\n")
        sub.text = sub.text.replace(" ◍", "")

    subs.save(os.path.join(dir_path, file))


def ask_chatgpt(prompt, settings):
    chatbot = Chatbot(config={"access_token": settings['access_token']})
    translate_prompt = """I want you to act as an Polish translator, spelling corrector and improver. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in Polish. I want you to replace my simplified C2-level words and sentences with more beautiful and elegant, upper level English words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations. Don't repeat yourself, diversity matters! Translate anime subtitles:

    """
    response = ""
    for message in chatbot.ask(translate_prompt + prompt):
        response = message["message"]
        print(response)
    return response

    # przykładowe uźycie

    # def ask_chatGPT(prompt):
    #     print("ChatGPT: ", end="")
    #     prev_text = ""
    #     for data in chatbot.ask(
    #         prompt
    #     ):
    #         prev_text = data["message"]
    #     # print(prev_text)
    #     return prev_text

    # prompt = "Co tam?"
    # # prompt = input("You: ")
    # while prompt != "Exit":
    #     print(ask_chatGPT(prompt))
    #     prompt = input("You: ")


def translate_srt(dir_path, file, settings):
    translator = settings['translator']
    translated_line_count = int(settings['translated_line_count'])
    alt_main_translator = settings['alt_main_translator']

    if alt_main_translator == 'no' and (dir_path.endswith('main_subs') or dir_path.endswith('alt_subs')):
        cprint("\nUwaga!", 'yellow', attrs=['bold'])
        print(
            f"Tłumaczenie folderów wyłączone.\nZakładam, że", end=' ')
        cprint(f"{file}", 'yellow', attrs=['bold'], end=' ')
        print("jest już przetłumaczony na polski.")
        return

    if translator == 'Google Translate':
        cprint("\nTłumaczenie za pomocą Google Translate... :",
               'yellow', attrs=['bold'], end=' ')
        print(file)
        translate_google(dir_path, file, translated_line_count)
    elif translator == 'DeepL API':
        cprint("\nTłumaczenie za pomocą DeepL API... :",
               'yellow', attrs=['bold'], end=' ')
        print(file)
        translate_deepl_api(dir_path, file, translated_line_count)
    elif translator == 'DeepL Desktop':
        cprint("\nTłumaczenie za pomocą DeepL Desktop... :",
               'yellow', attrs=['bold'], end=' ')
        print(file)
        translate_deepl_desktop(dir_path, file, translated_line_count)
        time.sleep(1)
        pyautogui.hotkey('alt', 'f4')
    elif translator == 'ChatGPT 3.5 Free':
        cprint("\nTłumaczenie za pomocą ChatGPT 3.5 Free... :",
               'yellow', attrs=['bold'], end=' ')
        print(file)
        translate_chatgpt_free(dir_path, file, translated_line_count, settings)

    cprint("Tłumaczenie zakończone.", 'green', attrs=['bold'])


    def srt_to_wav_harpo(self, tts_speed: str, tts_volume: str) -> None:
        self.ansi_srt()
        # Inicjalizacja silnika mowy
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if voice.name == 'Vocalizer Expressive Zosia Harpo 22kHz':
                engine.setProperty('voice', voice.id)
        engine.setProperty('rate', int(tts_speed))  # Szybkość mówienia
        engine.setProperty('volume', float(tts_volume))  # Głośność

        subtitles = pysrt.open(os.path.join(
            self.working_space_temp_main_subs, self.filename), encoding='ANSI')

        # Odczytanie napisów i zapisanie mowy do pliku WAV
        output_file = os.path.splitext(os.path.join(
            self.working_space_temp, self.filename))[0] + '.wav'
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(22500)  # 22kHz

            for i, subtitle in enumerate(subtitles, start=1):
                print(
                    f"{i}\n{subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitle.text}\n")

                start_time = subtitle.start.to_time()
                start_time = start_time.hour * 3600 + start_time.minute * \
                    60 + start_time.second + start_time.microsecond / 1000000
                # Zapisanie mowy do pliku WAV
                engine.save_to_file(subtitle.text, os.path.join(
                    self.working_space_temp, "temp.wav"))
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
                with wave.open(os.path.join(self.working_space_temp, "temp.wav"), 'rb') as temp_file:
                    data = temp_file.readframes(temp_file.getnframes())
                    wav_file.writeframes(data)

        # Usunięcie pliku tymczasowego
        os.remove(os.path.join(self.working_space_temp, "temp.wav"))


def process_subtitle(subtitle):
    i = subtitle.index
    start_time = subtitle.start.to_time().strftime('%H:%M:%S.%f')[:-3]
    end_time = subtitle.end.to_time().strftime('%H:%M:%S.%f')[:-3]
    text = subtitle.text
    print(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    time.sleep(0.02)


def srt_to_wav_balabolka(dir_path, tts_path, file, tts_speed, tts_volume):
    file_path = os.path.join(tts_path, file)
    with contextlib.suppress(UnicodeDecodeError):
        subtitles = pysrt.open(file_path, encoding='ANSI')
        balcon_path = os.path.join(dir_path, "src", "balabolka", "balcon.exe")
        output_wav_path = os.path.join(
            tts_path, os.path.splitext(file)[0] + ".wav")
        command = f'"{balcon_path}" -fr 48 -f "{file_path}" -w "{output_wav_path}" -n "IVONA 2 Agnieszka" -s {tts_speed} -v {tts_volume}'

        # Tworzenie wątku dla komendy
        command_thread = threading.Thread(
            target=execute_command, args=(command,))

        # Uruchamianie wątku dla komendy
        command_thread.start()

        # Wykonanie pętli w głównym wątku
        for i, subtitle in enumerate(subtitles, start=1):
            process_subtitle(subtitle)

        # Oczekiwanie na zakończenie wątku komendy
        command_thread.join()


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
            time.sleep(2)
    await asyncio.gather(*tasks)
    return mp3_files


def merge_audio_files(mp3_files, subtitles, dir_path):
    file_name = os.path.splitext(subtitles.path)[0]
    with wave.open(f"{file_name}.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)

        audio_segments = []
        for i, mp3_file in enumerate(mp3_files, start=1):
            print(
                f"{i}\n{subtitles[i-1].start.to_time().strftime('%H:%M:%S.%f')[:-3]} --> {subtitles[i-1].end.to_time().strftime('%H:%M:%S.%f')[:-3]}\n{subtitles[i-1].text}\n")

            mp3_file_path = os.path.join(dir_path, mp3_file)
            if os.path.isfile(mp3_file_path):
                start_time = subtitles[i-1].start.to_time()
                start_time = start_time.hour * 3600 + start_time.minute * \
                    60 + start_time.second + start_time.microsecond / 1000000
                sound = AudioSegment.from_file(mp3_file_path, format="mp3")
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


def srt_to_wav_edge_online(dir_path, file, tts, tts_speed, tts_volume):
    if tts == "TTS - Zofia - Edge":
        voice = "pl-PL-ZofiaNeural"
    elif tts == "TTS - Marek - Edge":
        voice = "pl-PL-MarekNeural"
    if tts_speed:
        rate = tts_speed
    if tts_volume:
        volume = tts_volume

    subtitles = pysrt.open(os.path.join(dir_path, file), encoding='ANSI')
    mp3_files = asyncio.run(generate_wav_files(subtitles, voice, rate, volume))
    merge_audio_files(mp3_files, subtitles, dir_path)


def tts_srt(dir_path, tts_path, file, settings):
    tts = settings['tts']
    tts_speed = settings['tts_speed']
    tts_volume = settings['tts_volume']

    cprint(
        "Rozpoczynam generowanie pliku audio... :",
        "yellow",
        attrs=["bold"],
        end=" ",
    )
    print(file)
    if tts == "TTS - Zosia - Harpo":
        srt_to_wav_harpo(tts_path, file, tts_speed, tts_volume)
    elif tts == "TTS - Agnieszka - Ivona":
        srt_to_wav_balabolka(dir_path, tts_path, file, tts_speed, tts_volume)
    elif tts in ["TTS - Zofia - Edge", "TTS - Marek - Edge"]:
        srt_to_wav_edge_online(tts_path, file, tts, tts_speed, tts_volume)
    cprint("\nGenerowanie pliku audio zakończone.", "yellow", attrs=["bold"])


def merge_tts_audio(dir_path, tmp_path, main_subs_path, lector_path):
    ffmpeg_path = os.path.join(dir_path, "src", "ffmpeg", "bin", "ffmpeg.exe")
    excluded_extensions = ["srt", "ass"]

    main_subs_files = [f.lower() for f in os.listdir(main_subs_path)]
    tmp_files = [f.lower() for f in os.listdir(tmp_path)]

    for file in os.listdir(tmp_path):
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext[1:].lower()

        if file_ext not in excluded_extensions and (file_name + ".wav").lower() in main_subs_files or (file_name + ".wav").lower() in tmp_files:
            file_path_1 = os.path.join(tmp_path, file)
            file_path_2 = os.path.join(main_subs_path, file_name + ".wav") if (
                file_name + ".wav").lower() in main_subs_files else os.path.join(tmp_path, file_name + ".wav")

            output_file = os.path.join(lector_path, file_name + ".eac3")

            if not os.path.exists(output_file):
                command = [
                    ffmpeg_path,
                    "-i", file_path_1,
                    "-i", file_path_2,
                    "-filter_complex", "[1:a]volume=7dB[a1];[0:a][a1]amix=inputs=2:duration=first",
                    output_file
                ]
                subprocess.call(command)

                os.remove(file_path_1)
                if file_path_2 != file_path_1:
                    os.remove(file_path_2)

    for file in os.listdir(main_subs_path):
        file_path = os.path.join(main_subs_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    for file in os.listdir(tmp_path):
        file_path = os.path.join(tmp_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def move_output_files(dir_path, alt_subs_path, lector_path, settings):
    for file in os.listdir(lector_path):
        file_path = os.path.join(lector_path, file)
        # przenieś plik z lektorem do katalogu docelowego
        destination_path = os.path.join(dir_path, file)
        shutil.move(file_path, destination_path)

    for file in os.listdir(alt_subs_path):
        file_path = os.path.join(alt_subs_path, file)
        if file.endswith('.ass') and settings['alt_main_translator'] == 'no':
            # przenieś plik ass
            destination_path = os.path.join(dir_path, file)
            shutil.move(file_path, destination_path)
        elif file.endswith('.srt') and settings['alt_main_translator'] == 'yes':
            # przenieś plik srt
            destination_path = os.path.join(dir_path, file)
            shutil.move(file_path, destination_path)

    # Opróżnij folder alt_subs_path
    shutil.rmtree(alt_subs_path)
    os.mkdir(alt_subs_path)


def marge_subtitles_and_lector(dir_path, subtitle_path, lector_path, mkv_file, tmp_path):
    mkvmerge_path = os.path.join(dir_path, "src", "mkvtoolnix", "mkvmerge.exe")
    output_file = os.path.join(tmp_path, mkv_file)

    command = [
        mkvmerge_path, '-o', output_file, '--no-subtitles', '--no-audio', os.path.join(
            dir_path, mkv_file), lector_path,
        '--language', '0:pol', '--track-name', '0:"Napisy Poboczne PL"', subtitle_path
    ]
    process = subprocess.Popen(command)
    cprint(
        f'Łączenie lektora i napisów do {mkv_file}', 'green', attrs=['bold'])
    process.communicate()
    if subtitle_path.endswith('.ass'):
        os.remove(subtitle_path[:-4] + '.srt')
    if subtitle_path.endswith('.srt'):
        os.remove(subtitle_path[:-4] + '.ass')
    os.remove(subtitle_path)
    os.remove(lector_path)


def marge_lector(dir_path, lector_path, mkv_file, tmp_path):
    mkvmerge_path = os.path.join(dir_path, "src", "mkvtoolnix", "mkvmerge.exe")
    output_file = os.path.join(tmp_path, mkv_file)

    command = [
        mkvmerge_path, '-o', output_file, '--no-subtitles', '--no-audio', os.path.join(
            dir_path, mkv_file),
        '--language', '0:pol', '--track-name', '0:"Lektor PL"', lector_path
    ]
    process = subprocess.Popen(command)
    cprint(f'Dodawanie lektora do {mkv_file}', 'green', attrs=['bold'])
    process.communicate()
    os.remove(lector_path)


def burn_subtitles(dir_path, tmp_path, file):
    for filename in os.listdir(tmp_path):
        if filename.endswith(".mkv") and filename == file:
            ffmpeg_path = os.path.join(
                dir_path, "src", "ffmpeg", "bin", "ffmpeg.exe")

            new_filename = re.sub(
                r'[^A-Za-z0-9.]+', '_', filename)

            os.rename(os.path.join(tmp_path, filename), new_filename)

            subprocess.call([ffmpeg_path, '-i', new_filename, '-c:v', 'libx264', '-crf', '54', '-preset',
                             'ultrafast', '-c:a', 'copy', '-vf', 'subtitles=' + new_filename, os.path.join(tmp_path, new_filename[:-4] + '_lektor.mp4')])
            os.remove(new_filename)
            os.rename(os.path.join(tmp_path, new_filename[:-4] + '_lektor.mp4'),
                      os.path.join(tmp_path, filename[:-4] + '_lektor.mp4'))
            dst_file = os.path.join(tmp_path, filename[:-4] + '_lektor.mp4')
            shutil.move(dst_file, dir_path)


def burn_lector(dir_path, tmp_path, file):
    ffmpeg_path = os.path.join(dir_path, "src", "ffmpeg", "bin", "ffmpeg.exe")

    tmp_path = os.path.join(tmp_path, file)
    mp4_path = os.path.join(dir_path, file.replace('.mkv', '_lektor.mp4'))

    command = [
        ffmpeg_path, '-i', tmp_path, '-c:v', 'libx264', '-crf', '54', '-preset', 'ultrafast', '-c:a', 'copy', mp4_path
    ]
    subprocess.run(command)
    os.remove(tmp_path)


def output_files(dir_path, alt_subs_path, lector_path, settings, tmp_path):
    output_option = settings["output"]
    if output_option == "Oglądam w MM_AVH_Players":
        print("Kopiuję pliki wyjściowe do folderu z filmem...")
        move_output_files(dir_path, alt_subs_path, lector_path, settings)
    else:

        for file in os.listdir(dir_path):
            if file.endswith('.mkv'):
                mkv_file = file
                base_name = os.path.splitext(mkv_file)[0]

                srt_file = f"{base_name}.srt"
                ass_file = f"{base_name}.ass"
                lector_file = f"{base_name}.eac3"

                srt_path = os.path.join(alt_subs_path, srt_file)
                ass_path = os.path.join(alt_subs_path, ass_file)
                lector_path_2 = os.path.join(lector_path, lector_file)

                if os.path.isfile(srt_path) and settings['alt_main_translator'] == 'yes':
                    marge_subtitles_and_lector(
                        dir_path, srt_path, lector_path_2, mkv_file, tmp_path)
                    if output_option == 'Scal do mkv':
                        output_file = os.path.join(tmp_path, mkv_file)
                        destination_path = os.path.join(dir_path, mkv_file)[
                            :-4] + '_lektor.mkv'
                        shutil.move(output_file, destination_path)
                    elif output_option == 'Wypal do mp4':
                        burn_subtitles(dir_path, tmp_path, file)

                elif os.path.isfile(ass_path) and settings['alt_main_translator'] == 'no':
                    marge_subtitles_and_lector(
                        dir_path, ass_path, lector_path_2, mkv_file, tmp_path)
                    if output_option == 'Scal do mkv':
                        output_file = os.path.join(tmp_path, mkv_file)
                        destination_path = os.path.join(dir_path, mkv_file)[
                            :-4] + '_lektor.mkv'
                        shutil.move(output_file, destination_path)
                    elif output_option == 'Wypal do mp4':
                        burn_subtitles(dir_path, tmp_path, file)
                else:
                    marge_lector(dir_path, lector_path_2, mkv_file, tmp_path)
                    if output_option == 'Scal do mkv':
                        output_file = os.path.join(tmp_path, mkv_file)
                        destination_path = os.path.join(dir_path, mkv_file)[
                            :-4] + '_lektor.mkv'
                        shutil.move(output_file, destination_path)
                    elif output_option == 'Wypal do mp4':
                        burn_lector(dir_path, tmp_path, file)


def main():
    cprint("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝\n",
           'white', attrs=['bold'])

    dir_path = directory_path()
    settings = get_settings(dir_path)

    if os.path.isfile(os.path.join(dir_path, 'src', 'settings.json')):
        cprint("Czy chcesz zmienić ustawienia? (t / y = tak):",
               'white', attrs=['bold'], end=" ")
        change_settings = input("")
        if change_settings.lower() in ['t', 'y', 'tak', 'yes']:
            set_settings(dir_path, settings)
        else:
            cprint("Nie zmieniono ustawień.\n", 'green', attrs=['bold'])
    else:
        cprint("Ustawienia wstępne.\n", 'green', attrs=['bold'])
        set_settings(dir_path, settings)

    # dla każdego pliku mkv w folderze wykonaj
    for file in os.listdir(dir_path):
        if file.endswith(".mkv"):
            mkv_extract(dir_path, file, mkv_info(dir_path, file))

    # dla każdego pliku ass w folderze wykonaj
    tmp_path = os.path.join(dir_path, 'src', 'tmp')
    alt_subs_path = os.path.join(tmp_path, 'alt_subs')
    main_subs_path = os.path.join(tmp_path, 'main_subs')
    lector_path = os.path.join(tmp_path, 'lector')

    # rozdzielanie napisów
    for file in os.listdir(tmp_path):
        if file.endswith(".ass"):
            split_ass(tmp_path, file)

    for file in os.listdir(tmp_path):
        if file.endswith(".ass"):
            ass_to_srt(tmp_path, file)
    for file in os.listdir(alt_subs_path):
        if file.endswith(".ass"):
            ass_to_srt(alt_subs_path, file)
    for file in os.listdir(main_subs_path):
        if file.endswith(".ass"):
            ass_to_srt(main_subs_path, file)

    # Tłumaczenie i ANSI
    for file in os.listdir(tmp_path):
        if file.endswith('.srt'):
            translate_srt(tmp_path, file, settings)
            asnii_srt(tmp_path, file)
            tts_srt(dir_path, tmp_path, file, settings)
    for file in os.listdir(alt_subs_path):
        if file.endswith('.srt'):
            translate_srt(alt_subs_path, file, settings)
            asnii_srt(alt_subs_path, file)
    for file in os.listdir(main_subs_path):
        if file.endswith('.srt'):
            translate_srt(main_subs_path, file, settings)
            asnii_srt(main_subs_path, file)
            tts_srt(dir_path, main_subs_path, file, settings)

    merge_tts_audio(dir_path, tmp_path, main_subs_path, lector_path)
    output_files(dir_path, alt_subs_path, lector_path, settings, tmp_path)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time

    seconds = int(execution_time % 60)
    minutes = int((execution_time // 60) % 60)
    hours = int(execution_time // 3600)

    print("Czas wykonania: {} godzin, {} minut, {} sekund".format(
        hours, minutes, seconds))

 # option = {
    #     1:
    # }
    # cprint("╚═══════════════ WYBIERZ OPCJĘ ════════════════╝",
    #        'white', attrs=['bold'])
    # print("1. Ustawienia")
    # print("2. EPIC AUTO: Ekstrakcja -> Tłumaczenie -> Lektor ->\n   Scalanie lektora z audio ->\n   (opcjonalnie) Scalenie do wideo z napisami / napisami pobocznymi ->\n   Wypalenie napisów do wideo do formatu mp4\n   LUB Zapisanie lektor-audio oraz napisów pobocznych do folderu z filmem")
    # cprint("\n╚═════════════════════ MKV ════════════════════╝",
    #        'white', attrs=['bold'])
    # print("3. Informacje o plikach mkv")
    # print("4. Ekstrakcja napisów / ścieżki dźwiękowej / obrazu")
    # print("5. Ekstrakcja fontów")
    # print("6. Scalanie napisów / audio do mkv")
    # cprint("\n╚════════════════ TEKST ~ AUDIO ═══════════════╝",
    #        'white', attrs=['bold'])
    # print("6. Tłumaczenie napisów i tekstów")
    # print("7. Teksy na mowę")
    # print("8. Scalanie audio z lektorem do jednego pliku audio")
    # cprint("\n╚══════════════ WYPALENIE DO MP4 ═══════════════╝",
    #        'white', attrs=['bold'])
    # print("9. Lektor do wideo")
    # print("10. Wypalanie napisów do wideo")
    # print("11. Wypalanie napisów pobocznych do wideo")
    # 1. Ekstrakcja
    # 2. W zalerzności języka w subtitles w lang lub lang_ietf przetłumacz na polski lub nie w przypadku und pytaj użytkownika czy tłumaczyć
    # 3. Zrobienie lektora
    # 4. Połączenie audio z lektorem
    # 6. Wypal napisy do wideo
    # 7. Dodaj ścieżkę dźwiękową lektora do wideo
    # 8. Wypal napisy i dodaj ścieżkę dźwiękową lektora do wideo
    # 9. Nałóż na siebie dwie ścieżki dźwiękowe
    # dir_path\src\ffmpeg\bin
    # dir_path\src\mkvtoolnix\mkvinfo.exe
    # dir_path\src\mkvtoolnix\mkvextract.exe
    # dir_path\src\mkvtoolnix\mkvmerge.exe
    # dir_path\src\mkvtoolnix\mkvpropedit.exe
    # dir_path\src\mkvtoolnix\mkvtoolnix-gui.exe

    # [2023-05-25][12:24:19]   "tracks": [
    # [2023-05-25][12:24:19]     {
    # [2023-05-25][12:24:19]       "codec": "AVC/H.264/MPEG-4p10",
    # [2023-05-25][12:24:19]       "id": 0,
    # [2023-05-25][12:24:19]       "properties": {
    # [2023-05-25][12:24:19]         "codec_id": "V_MPEG4/ISO/AVC",
    # [2023-05-25][12:24:19]         "codec_private_data": "01640028ffe1001c67640028acb280f0044fcb80b50101014000001f400005da83c60c9601000768e930332c8b00fdf8f800",
    # [2023-05-25][12:24:19]         "codec_private_length": 50,
    # [2023-05-25][12:24:19]         "default_duration": 41708333,
    # [2023-05-25][12:24:19]         "default_track": true,
    # [2023-05-25][12:24:19]         "display_dimensions": "1920x1080",
    # [2023-05-25][12:24:19]         "display_unit": 0,
    # [2023-05-25][12:24:19]         "enabled_track": true,
    # [2023-05-25][12:24:19]         "forced_track": false,
    # [2023-05-25][12:24:19]         "language": "und",
    # [2023-05-25][12:24:19]         "language_ietf": "und",
    # [2023-05-25][12:24:19]         "minimum_timestamp": 0,
    # [2023-05-25][12:24:19]         "number": 1,
    # [2023-05-25][12:24:19]         "packetizer": "mpeg4_p10_video",
    # [2023-05-25][12:24:19]         "pixel_dimensions": "1920x1080",
    # [2023-05-25][12:24:19]         "uid": 1
    # [2023-05-25][12:24:19]       },
    # [2023-05-25][12:24:19]       "type": "video"
    # [2023-05-25][12:24:19]     },
