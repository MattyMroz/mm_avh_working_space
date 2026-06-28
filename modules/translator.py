"""
    The SubtitleTranslator class is this module is used for translating subtitles from one language to another.
        TThe target language is Polish in methods throughout the class

    * Example: Frist create an instance of the SubtitleTranslator class:
        subtitle_tool = SubtitleTranslator()

    * Example usage for translating subtitles using Google Translate:
        subtitle_tool.translate_google("sample_subtitle.srt", "/path/to/directory", 100)

    * Example usage for translating subtitles using the DeepL API:
        subtitle_tool.translate_deepl_api("sample_subtitle.srt", "/path/to/directory", 100, "your_deepl_api_key")

    * Example usage for translating subtitles using the desktop version of DeepL:
        subtitle_tool.translate_deepl_desktop("sample_subtitle.srt", "/path/to/directory", 100)

    * Example usage for selecting the appropriate translation method based on the settings and translating the subtitles:
        Settings.change_settings_save_to_file()
        settings = Settings.load_from_file() | (Settings(translator="Google Translate", translated_line_count="100"))
        subtitle_tool.translate_srt("sample_subtitle.srt", "/path/to/directory", settings)
"""

import re
from asyncio import run as asyncio_run
from dataclasses import dataclass
from os import environ, path
from subprocess import call
from time import sleep
from typing import List

import deepl
import pyautogui
import pyperclip
import pysrt
from googletrans import Translator

from constants import (
    WORKING_SPACE_TEMP_MAIN_SUBS,
    WORKING_SPACE_TEMP_ALT_SUBS,
    console)
from data.settings import Settings


@dataclass(slots=True)
class SubtitleTranslator:
    """
        The SubtitleTranslator class is used for translating subtitles from one language to another.

        Attributes:
            - working_space_temp_main_subs (str): Path to the folder with main subtitles.
            - working_space_temp_alt_subs (str): Path to the folder with alternative subtitles.

        Methods:
            - translate_google(filename: str, dir_path: str, translated_line_count: int, is_combined_with_gpt: bool = False) -> pysrt.SubRipFile:
                Translates subtitles using Google Translate.

            - translate_deepl_api(filename: str, dir_path: str, translated_line_count: int, deepl_api_key: str) -> None:
                Translates subtitles using the DeepL API.

            - translate_deepl_desktop(filename: str, dir_path: str, translated_line_count: int) -> None:
                Translates subtitles using the desktop version of DeepL.

            - translate_srt(filename: str, dir_path: str, settings: Settings) -> None:
                Selects the appropriate translation method based on the settings and translates the subtitles.
    """

    working_space_temp_main_subs: str = WORKING_SPACE_TEMP_MAIN_SUBS
    working_space_temp_alt_subs: str = WORKING_SPACE_TEMP_ALT_SUBS

    @staticmethod
    def translate_google(filename: str, dir_path: str, translated_line_count: int, is_combined_with_gpt: bool = False) -> pysrt.SubRipFile:
        """
            Translates subtitles using Google Translate.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
                - is_combined_with_gpt (bool, optional): Whether to combine with GPT for translation. Defaults to False.

            Returns:
                - pysrt.SubRipFile: The translated subtitle file.
        """
        # Wrapper function to handle async googletrans v4+
        async def _translate_async(text: str, dest: str = 'pl') -> str:
            translator = Translator()
            result = await translator.translate(text, dest=dest)
            return result.text
        
        def translate_sync(text: str, dest: str = 'pl') -> str:
            """Synchronous wrapper for async translate"""
            return asyncio_run(_translate_async(text, dest))
        
        subs: pysrt.SubRipFile = pysrt.open(path.join(dir_path, filename), encoding='utf-8')

        SEPARATOR: str = "\u200B###\u200B"
        NEWLINE_MARKER: str = "\u200B##\u200B"

        translated_subs: List[str] = []
        subs_combined: List[str] = []

        for i, sub in enumerate(subs):
            subs_combined.append(sub.text.replace("\n", NEWLINE_MARKER))

            if (i + 1) % translated_line_count == 0 or i == len(subs) - 1:
                combined_text: str = SEPARATOR.join(subs_combined)
                translated_text: str = translate_sync(combined_text, dest='pl')

                translated_texts: List[str] = translated_text.split(SEPARATOR)

                if len(translated_texts) != len(subs_combined):
                    combined_text2: str = "\n".join(subs_combined)
                    translated_text2: str = translate_sync(combined_text2, dest='pl')
                    translated_texts = translated_text2.split("\n")

                if len(translated_texts) != len(subs_combined):
                    translated_texts = []
                    for single in subs_combined:
                        t: str = translate_sync(single, dest='pl')
                        translated_texts.append(t)

                if len(translated_texts) == len(subs_combined):
                    for t in translated_texts:
                        t = t.replace("\u200B", "")
                        nl_plain = NEWLINE_MARKER.replace("\u200B", "")
                        sep_plain = SEPARATOR.replace("\u200B", "")

                        t = (t.replace(nl_plain + ", ", ",\n")
                               .replace(nl_plain, "\n")
                               .replace(NEWLINE_MARKER + ", ", ",\n")
                               .replace(NEWLINE_MARKER, "\n")
                               .replace(sep_plain, "\n")
                               .replace("###", ""))

                        t = re.sub(r"[ \t]+\n", "\n", t)
                        t = re.sub(r"\n[ \t]+", "\n", t)
                        t = t.strip()
                        translated_subs.append(t)
                else:
                    for _ in subs_combined:
                        translated_subs.append("")

                subs_combined = []

        # Assign translations back to subtitles (safeguard index errors)
        if len(translated_subs) != len(subs):
            console.print(f"Ostrzeżenie: liczba przetłumaczonych wierszy ({len(translated_subs)}) != oryginał ({len(subs)}). Przypisuję liniowo i uzupełniam brakujące.", style='yellow_bold')

        for i, sub in enumerate(subs):
            if i < len(translated_subs):
                sub.text = translated_subs[i]
            else:
                # fallback: leave original text if missing
                sub.text = sub.text

        if is_combined_with_gpt:
            translated_filename: str = filename.replace(
                '.srt', '_translated_temp.srt')
            subs.save(path.join(dir_path, translated_filename))
            return subs
        subs.save(path.join(dir_path, filename))

    @staticmethod
    def translate_deepl_api(filename: str, dir_path: str, translated_line_count: int, deepl_api_key: str) -> None:
        """
            Translates subtitles using the DeepL API.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
                - deepl_api_key (str): The API key for the DeepL translator.
        """
        subs: pysrt.SubRipFile = pysrt.open(
            path.join(dir_path, filename), encoding='utf-8')
        translator: deepl.Translator = deepl.Translator(deepl_api_key)
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]
        for group in groups:
            text: str = " @@\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                                     for sub in group)
            translated_text: str = translator.translate_text(
                text, target_lang='PL').text
            translated_texts: List[str] = translated_text.split(" @@\n")
            if len(translated_texts) == len(group):
                for i in range(len(group)):
                    if i < len(translated_texts):
                        group[i].text = translated_texts[i]
                        group[i].text = group[i].text.replace(" ◍◍◍◍, ", ",\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍ ", "\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍", "")
        subs.save(path.join(dir_path, filename), encoding='utf-8')

    @staticmethod
    def translate_deepl_desktop(filename: str, dir_path: str, translated_line_count: int) -> None:
        """
            Translates subtitles using the desktop version of DeepL.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
        """
        command: str = path.join(
            environ['APPDATA'], 'Programs', 'Zero Install', '0install-win.exe')
        args: List[str] = ["run", "--no-wait",
                           "https://appdownload.deepl.com/windows/0install/deepl.xml"]
        call([command] + args)

        sleep(7)

        def auto_steps():
            screen_width, screen_height = pyautogui.size()
            x_coordinate = screen_width * 0.25
            y_coordinate = screen_height * 0.5
            pyautogui.moveTo(x_coordinate, y_coordinate)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('del')
            pyautogui.hotkey('ctrl', 'v')
            sleep(6)
            x_coordinate = screen_width * 0.75
            pyautogui.moveTo(x_coordinate, y_coordinate)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')

        subs: pysrt.SubRipFile = pysrt.open(
            path.join(dir_path, filename), encoding='utf-8')
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]

        for group in groups:
            text: str = " @@\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                                     for sub in group)
            text = text.rstrip('\n')
            pyperclip.copy(text)
            auto_steps()

            translated_text: str = pyperclip.paste()
            if translated_text:
                for sub, trans_text in zip(group, translated_text.split(" @@\n")):
                    sub.text = trans_text.replace(" ◍◍◍◍, ", ",\n")
                    sub.text = trans_text.replace(" ◍◍◍◍ ", "\n")
                    sub.text = trans_text.replace(" ◍◍◍◍", "")
        pyautogui.hotkey('alt', 'f4')

        subs.save(path.join(dir_path, filename), encoding='utf-8')

        frezes: List[str] = ["\nPrzetłumaczono z www.DeepL.com/Translator (wersja darmowa)\n",
                             "Przetłumaczono z www.DeepL.com/Translator (wersja darmowa)",
                             "\nTranslated with www.DeepL.com/Translator (free version)\n",
                             "\nTranslated with www.DeepL.com/Translator (free version)"]

        with open(path.join(dir_path, filename), 'r', encoding='utf-8') as in_file:
            text: str = in_file.read()

        for freze in frezes:
            text = text.replace(freze, "")

        with open(path.join(dir_path, filename), 'w', encoding='utf-8') as out_file:
            out_file.write(text)

    def translate_srt(self,  filename: str, dir_path: str, settings: Settings) -> None:
        """
            Selects the appropriate translation method based on the settings and translates the subtitles.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - settings (Settings): The settings for the translation.
        """
        translator: str = settings.translator
        translated_line_count: int = int(settings.translated_line_count)
        deepl_api_key: str = settings.deepl_api_key

        console.print(
            f"[green_italic]Tłumaczenie napisów za pomocą {translator}...")
        console.print(path.join(dir_path, filename), '\n', style='white_bold')

        translator_functions = {
            'Google Translate': lambda *args:
                SubtitleTranslator.translate_google(*args[:3]),
            'DeepL API': lambda *args:
                SubtitleTranslator.translate_deepl_api(
                    *args[:3], deepl_api_key),
            'DeepL Desktop Free': lambda *args:
                SubtitleTranslator.translate_deepl_desktop(*args[:3]),
        }

        if translator in translator_functions:
            translator_functions[translator](
                filename, dir_path, translated_line_count)
        else:
            console.print(
                f"Nieznany translator: {translator}", style='red_bold')
