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
from typing import Dict, List

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
    def _open_subs(file_path: str) -> pysrt.SubRipFile:
        """Open an SRT file, tolerating files already converted to ANSI.

        The TTS step rewrites subtitles in place as ANSI (cp1250), so a file
        that went through it is no longer valid UTF-8 and fails on the first
        Polish character. Fall back to cp1250 in that case.

        Args:
            file_path: Full path to the subtitle file.

        Returns:
            The parsed subtitle file.
        """
        try:
            return pysrt.open(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            return pysrt.open(file_path, encoding='cp1250')

    @staticmethod
    def _read_text(file_path: str) -> str:
        """Read a subtitle file as text, tolerating ANSI-encoded files.

        Args:
            file_path: Full path to the subtitle file.

        Returns:
            The file contents.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1250') as file:
                return file.read()

    @staticmethod
    def _clean_subtitle_text(text: str) -> str:
        """Strip leftover markup before translation, keeping line breaks intact.

        Removes ASS override tags ({...}) and any stray HTML tags that survived
        the ASS->SRT conversion, and turns the ASS hard space (\\h) into a normal
        space. Real newlines are preserved — the translators encode them with
        their own markers, so they must reach this point untouched.

        Args:
            text: Raw subtitle line text.

        Returns:
            The text with markup removed and newlines preserved.
        """
        text = re.sub(r'\{[^}]*\}', '', text)   # ASS override tags
        text = re.sub(r'<[^>]*>', '', text)     # stray HTML tags
        text = text.replace('\\h', ' ')          # ASS hard space
        return text

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
        
        subs: pysrt.SubRipFile = SubtitleTranslator._open_subs(
            path.join(dir_path, filename))

        ZWSP: str = "\u200B"  # zero-width space wrapping the markers
        SEPARATOR: str = f"{ZWSP}###{ZWSP}"
        NEWLINE_MARKER: str = f"{ZWSP}##{ZWSP}"

        def _clean_translation(t: str) -> str:
            """Undo the newline/separator markers and tidy whitespace."""
            nl_plain = NEWLINE_MARKER.replace(ZWSP, "")
            sep_plain = SEPARATOR.replace(ZWSP, "")
            t = t.replace(ZWSP, "")
            t = (t.replace(nl_plain + ", ", ",\n")
                   .replace(nl_plain, "\n")
                   .replace(NEWLINE_MARKER + ", ", ",\n")
                   .replace(NEWLINE_MARKER, "\n")
                   .replace(sep_plain, "\n")
                   .replace("###", ""))
            t = re.sub(r"[ \t]+\n", "\n", t)
            t = re.sub(r"\n[ \t]+", "\n", t)
            return t.strip()

        def _translate_unique(unique_texts: List[str]) -> List[str]:
            """Translate texts in batches of translated_line_count, 3-level fallback."""
            results: List[str] = []
            for start in range(0, len(unique_texts), translated_line_count):
                batch: List[str] = unique_texts[start:start + translated_line_count]
                combined_text: str = SEPARATOR.join(batch)
                translated_text: str = translate_sync(combined_text, dest='pl')
                translated_texts: List[str] = translated_text.split(SEPARATOR)

                if len(translated_texts) != len(batch):
                    combined_text2: str = "\n".join(batch)
                    translated_text2: str = translate_sync(combined_text2, dest='pl')
                    translated_texts = translated_text2.split("\n")

                if len(translated_texts) != len(batch):
                    translated_texts = [translate_sync(s, dest='pl') for s in batch]

                if len(translated_texts) == len(batch):
                    results.extend(_clean_translation(t) for t in translated_texts)
                else:
                    results.extend("" for _ in batch)
            return results

        # Translate each UNIQUE cleaned phrase once (newlines encoded with the
        # marker), then fill every line from the shared map — a phrase repeated
        # 1000 times costs one translation, not a thousand.
        marked_lines: List[str] = [
            SubtitleTranslator._clean_subtitle_text(sub.text).replace("\n", NEWLINE_MARKER)
            for sub in subs
        ]
        unique_marked: List[str] = list(dict.fromkeys(m for m in marked_lines if m.strip()))
        translation_map: Dict[str, str] = dict(
            zip(unique_marked, _translate_unique(unique_marked)))

        for sub, marked in zip(subs, marked_lines):
            sub.text = "" if not marked.strip() else (translation_map.get(marked) or sub.text)

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
        subs: pysrt.SubRipFile = SubtitleTranslator._open_subs(
            path.join(dir_path, filename))
        translator: deepl.Translator = deepl.Translator(deepl_api_key)

        NEWLINE_MARKER: str = " ◍◍◍◍ "
        SEPARATOR: str = " @@\n"

        def _clean_translation(t: str) -> str:
            """Undo the newline markers used to protect line breaks in a batch."""
            return (t.replace(" ◍◍◍◍, ", ",\n")
                     .replace(" ◍◍◍◍ ", "\n")
                     .replace(" ◍◍◍◍", ""))

        def _translate_unique(unique_texts: List[str]) -> List[str]:
            """Translate texts in batches of translated_line_count via DeepL."""
            results: List[str] = []
            for start in range(0, len(unique_texts), translated_line_count):
                batch: List[str] = unique_texts[start:start + translated_line_count]
                text: str = SEPARATOR.join(batch)
                translation_result = translator.translate_text(text, target_lang='PL')
                if isinstance(translation_result, list):
                    translated_text: str = "".join(r.text for r in translation_result)
                else:
                    translated_text = translation_result.text
                translated_texts: List[str] = translated_text.split(SEPARATOR)
                if len(translated_texts) == len(batch):
                    results.extend(_clean_translation(t) for t in translated_texts)
                else:
                    # Length mismatch — keep originals for this batch (no crash).
                    results.extend(batch)
            return results

        # Translate each UNIQUE cleaned phrase once, then fill every line from the
        # shared map — repeated phrases cost one translation, not one per line.
        marked_lines: List[str] = [
            SubtitleTranslator._clean_subtitle_text(sub.text).replace("\n", NEWLINE_MARKER)
            for sub in subs
        ]
        unique_marked: List[str] = list(dict.fromkeys(m for m in marked_lines if m.strip()))
        translation_map: Dict[str, str] = dict(
            zip(unique_marked, _translate_unique(unique_marked)))

        for sub, marked in zip(subs, marked_lines):
            sub.text = "" if not marked.strip() else (translation_map.get(marked) or sub.text)

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

        subs: pysrt.SubRipFile = SubtitleTranslator._open_subs(
            path.join(dir_path, filename))
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

        text = SubtitleTranslator._read_text(path.join(dir_path, filename))

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
        translator: str = settings.translator or ""
        translated_line_count: int = int(settings.translated_line_count or "0")
        deepl_api_key: str = settings.deepl_api_key or ""

        console.print(
            f"[green_italic]Tłumaczenie napisów za pomocą {translator}...")
        console.print(path.join(dir_path, filename), '\n', style='white_bold')

        def _translate_google(fname: str, directory: str, line_count: int) -> None:
            SubtitleTranslator.translate_google(fname, directory, line_count)

        def _translate_deepl_api(fname: str, directory: str, line_count: int) -> None:
            SubtitleTranslator.translate_deepl_api(
                fname, directory, line_count, deepl_api_key)

        translator_functions = {
            'Google Translate': _translate_google,
            'DeepL API': _translate_deepl_api,
        }

        if translator in translator_functions:
            translator_functions[translator](
                filename, dir_path, translated_line_count)
        else:
            console.print(
                f"Nieznany translator: {translator}", style='red_bold')
