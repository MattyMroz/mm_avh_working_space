"""
    The SubtitleRefactor class in this module provides various utilities for working with subtitle files.

    It can be used in different scenarios to perform tasks such as splitting ASS subtitle files, converting subtitles to different formats, and organizing files.

    * Example usage for splitting an ASS subtitle file based on styles:
        subtitle_tool = SubtitleRefactor("sample_subtitle.ass")
        subtitle_tool.split_ass()

    * Example usage for converting ASS subtitles to SRT format:
        subtitle_tool = SubtitleRefactor("sample_subtitle.ass")
        subtitle_tool.ass_to_srt()

    * Example usage for moving an SRT subtitle file to a specified directory:
        subtitle_tool = SubtitleRefactor("sample_subtitle.srt")
        subtitle_tool.move_srt()

    * Example usage for converting a text file to SRT format and performing other operations:
        subtitle_tool = SubtitleRefactor("sample_text.txt")
        subtitle_tool.txt_to_srt(1)

    * Example usage for converting numbers in an SRT subtitle file to their word equivalents in Polish:
        subtitle_tool = SubtitleRefactor("sample_subtitle.srt")
        subtitle_tool.convert_numbers_in_srt()

    * Example usage for updating subtitles in an existing ASS file using translated subtitles from an SRT file:
        subtitle_tool = SubtitleRefactor("sample_subtitle.srt")
        subtitle_tool.srt_to_ass()
"""

import re
from contextlib import suppress
from dataclasses import dataclass
from os import makedirs, path, remove, stat
from shutil import move
from typing import List, Tuple

from nltk.tokenize import sent_tokenize
from pyasstosrt import Subtitle
from pysubs2 import load, SSAEvent, SSAFile

from constants import (WORKING_SPACE,
                       WORKING_SPACE_OUTPUT,
                       WORKING_SPACE_TEMP,
                       WORKING_SPACE_TEMP_MAIN_SUBS,
                       WORKING_SPACE_TEMP_ALT_SUBS,
                       console)

from utils.number_in_words import NumberInWords


@dataclass(slots=True)
class SubtitleRefactor:
    """
        The SubtitleRefactor class is used for manipulating subtitle files. It provides functionalities such as splitting ASS subtitle files based on styles, converting ASS subtitles to SRT format, and moving SRT files to a specified directory.

        Attributes:
            - filename (str): The name of the subtitle file to be processed.
            - working_space (str, optional): The directory where the subtitle file is located.
            - working_space_output (str, optional): The directory where the output files will be saved.
            - working_space_temp (str, optional): The directory where temporary files will be saved during processing.
            - working_space_temp_main_subs (str, optional): The directory for main subtitles during processing.
            - working_space_temp_alt_subs (str, optional): The directory for alternate subtitles during processing.

        Methods:
            - split_ass(self) -> None: Splits an ASS subtitle file into two files based on selected styles.
            - ass_to_srt(self) -> None: Converts ASS subtitle files to SRT format.
            - move_srt(self) -> None: Moves an SRT subtitle file to a specified directory.
            - txt_to_srt(self, lines_per_caption: int) -> None: Converts a text file to SRT (SubRip Text) format.
            - convert_numbers_in_srt(self) -> None: Converts numbers in an SRT subtitle file to their word equivalents in Polish.
            - srt_to_ass(self) -> None: Updates subtitles in an existing ASS file using translated subtitles from an SRT file. If the ASS file does not exist, the SRT file is moved to the output directory, and its extension is changed to .ass. After these operations, the original ASS and SRT files are deleted.
    """
    filename: str
    working_space: str = WORKING_SPACE
    working_space_output: str = WORKING_SPACE_OUTPUT
    working_space_temp: str = WORKING_SPACE_TEMP
    working_space_temp_main_subs = WORKING_SPACE_TEMP_MAIN_SUBS
    working_space_temp_alt_subs = WORKING_SPACE_TEMP_ALT_SUBS

    def split_ass(self) -> None:
        """
            Splits an ASS subtitle file into two files based on selected styles.
        """
        self._create_directories()
        subs: SSAFile = self._load_subs()
        styles: List[str] = self._get_styles(subs)
        self._display_styles(styles)
        selected_styles: List[str] = self._select_styles(styles)
        if not selected_styles:
            self._move_subs_to_main()
            return
        main_subs, alt_subs = self._split_subs(subs, selected_styles)
        self._copy_metadata_and_styles(
            subs, main_subs, alt_subs, selected_styles)
        self._save_subs(main_subs, alt_subs, subs, selected_styles)
        self._remove_source_file()
        console.print("Podział napisów zakończony pomyślnie.",
                      style='green_bold')

    def _create_directories(self) -> None:
        """
            Creates directories if they do not exist.
        """
        if not path.exists(self.working_space_temp_main_subs):
            makedirs(self.working_space_temp_main_subs, exist_ok=True)
        if not path.exists(self.working_space_temp_alt_subs):
            makedirs(self.working_space_temp_alt_subs, exist_ok=True)

    def _load_subs(self) -> SSAFile:
        """
            Loads the subtitle file.
        """
        with open(path.join(self.working_space_temp, self.filename), 'r', encoding='utf-8') as file:
            return SSAFile.from_file(file)

    def _get_styles(self, subs: SSAFile) -> List[str]:
        """
            Returns a list of styles in the subtitle file.
        """
        styles: List[str] = []
        for event in subs:
            if event.style not in styles:
                styles.append(event.style)
        return styles

    def _display_styles(self, styles: List[str]) -> None:
        """
            Displays the styles to the user.
        """
        console.print("PODZIAŁ PLIKU:", style='yellow_bold')
        console.print(self.filename, style='white_bold')
        console.print("Dostępne style do TTS:", style='yellow_bold')
        for i, style in enumerate(styles, start=1):
            console.print(
                f"[yellow_bold]{i}.[/yellow_bold] {style}", style='white_bold')

    def _select_styles(self, styles: List[str]) -> List[str]:
        """
            Prompts the user to select styles and returns a list of selected styles.
        """
        selected_styles: List[str] = []
        while True:
            console.print("Wybierz style do zapisu (naciśnij ENTER, aby zakończyć):",
                          style='green_bold', end=" ")
            selection: str = input('')
            if not selection:
                break
            with suppress(ValueError):
                selected_index: int = int(selection) - 1
                if 0 <= selected_index < len(styles):
                    selected_styles.append(styles[selected_index])
        return selected_styles

    def _move_subs_to_main(self) -> None:
        """
            Moves the subtitle file to the main_subs directory.
        """
        console.print("Nie wybrano żadnych stylów. Przeniesiono napisów do main_subs.",
                      style='red_bold')
        makedirs(self.working_space_temp_main_subs, exist_ok=True)
        alt_file_path: str = path.join(
            self.working_space_temp, self.filename)
        main_file_path: str = path.join(
            self.working_space_temp_main_subs, self.filename)
        move(alt_file_path, main_file_path)

    def _split_subs(self, subs: SSAFile, selected_styles: List[str]) -> Tuple[SSAFile, SSAFile]:
        """
            Splits the subtitle file into two files based on the selected styles.
        """
        main_subs: SSAFile = SSAFile()
        alt_subs: SSAFile = SSAFile()

        for event in subs:
            if event.style in selected_styles:
                main_subs.append(event)
            else:
                alt_subs.append(event)

        return main_subs, alt_subs

    def _copy_metadata_and_styles(self, subs: SSAFile, main_subs: SSAFile, alt_subs: SSAFile, selected_styles: List[str]) -> None:
        """
            Copies metadata and styles to the output files.
        """
        main_subs.info = subs.info
        alt_subs.info = subs.info

        main_style_names: List[str] = [style_name for style_name in subs.styles.keys()
                                       if style_name in selected_styles]
        main_subs.styles.clear()
        for style_name in main_style_names:
            main_subs.styles[style_name] = subs.styles[style_name]

        alt_style_names: List[str] = [style_name for style_name in subs.styles.keys()
                                      if style_name not in selected_styles]
        alt_subs.styles.clear()
        for style_name in alt_style_names:
            alt_subs.styles[style_name] = subs.styles[style_name]

    def _save_subs(self, main_subs: SSAFile, alt_subs: SSAFile, subs: SSAFile, selected_styles: List[str]) -> None:
        """
            Saves the split subtitle files.
        """
        main_output_file: str = path.join(
            self.working_space_temp_main_subs, self.filename)
        alt_output_file: str = path.join(
            self.working_space_temp_alt_subs, self.filename)

        main_subs.info = subs.info
        alt_subs.info = subs.info

        main_style_names: List[str] = [style_name for style_name in subs.styles.keys()
                                       if style_name in selected_styles]
        main_subs.styles.clear()
        for style_name in main_style_names:
            main_subs.styles[style_name] = subs.styles[style_name]

        alt_style_names: List[str] = [style_name for style_name in subs.styles.keys()
                                      if style_name not in selected_styles]
        alt_subs.styles.clear()
        for style_name in alt_style_names:
            alt_subs.styles[style_name] = subs.styles[style_name]

        with open(main_output_file, 'w', encoding='utf-8') as main_file:
            main_file.write(main_subs.to_string(format_='ass'))

        with open(alt_output_file, 'w', encoding='utf-8') as alt_file:
            alt_file.write(alt_subs.to_string(format_='ass'))

    def _remove_source_file(self) -> None:
        """
            Removes the source subtitle file.
        """
        remove(path.join(self.working_space_temp, self.filename))

    def ass_to_srt(self) -> None:
        """
            Converts ASS subtitle files to SRT format and removes HTML tags.
        """
        folders = [self.working_space_temp_main_subs,
                   self.working_space_temp_alt_subs]
        for folder in folders:
            file_path: str = path.join(folder, self.filename)

            if not path.exists(file_path):
                continue

            ass_subs = SSAFile.load(file_path)
            srt_subs = SSAFile()

            for i, sub in enumerate(ass_subs):
                srt_subs.insert(i, sub)

            srt_content = srt_subs.to_string(format_='srt')
            srt_content = re.sub(r'<.*?>', '', srt_content)

            with open(file_path.replace('.ass', '.srt'), 'w', encoding='utf-8') as file:
                file.write(srt_content)

        console.print()

    def move_srt(self) -> None:
        """
            Moves an SRT subtitle file to a specified directory and removes HTML tags.
        """
        target_file_path: str = path.join(
            self.working_space_temp_main_subs, self.filename)

        if not path.exists(self.working_space_temp_main_subs):
            makedirs(self.working_space_temp_main_subs, exist_ok=True)

        source_file_path: str = path.join(
            self.working_space_temp, self.filename)

        # Otwórz plik źródłowy i przeczytaj jego zawartość
        with open(source_file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Usuń znaczniki HTML
        file_content = re.sub(r'<.*?>', '', file_content)

        # Zapisz zmodyfikowaną zawartość do pliku docelowego
        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(file_content)

        # Usuń plik źródłowy
        remove(source_file_path)

    def txt_to_srt(self, lines_per_caption: int) -> None:
        """
        Converts a text file to SRT (SubRip Text) format.

        This method reads a text file, tokenizes the text into sentences using the NLTK library, and writes the sentences into a new SRT file. Groups of sentences are combined into a single caption based on the 'lines_per_caption' parameter. Each group becomes a separate subtitle in the SRT file. The original text file is then deleted, and the filename attribute of the class instance is updated to the new SRT file. Finally, the SRT file is moved to the 'main_subs' directory.

        Args:
            lines_per_caption (int): The number of sentences to include in each caption.

        """
        txt_file_path: str = path.join(self.working_space_temp, self.filename)
        srt_file_path: str = txt_file_path.replace('.txt', '.srt')

        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text: str = file.read()

        sentences: List[str] = sent_tokenize(text)

        subs: SSAFile = SSAFile()
        for i in range(0, len(sentences), lines_per_caption):
            caption = ' '.join(sentences[i:i+lines_per_caption]).strip()
            event: SSAEvent = SSAEvent(start=0, end=0, text=caption)
            subs.append(event)

        with open(srt_file_path, 'w', encoding='utf-8') as file:
            file.write(subs.to_string(format_='srt'))

        remove(txt_file_path)

        self.filename = self.filename.replace('.txt', '.srt')
        self.move_srt()

    def convert_numbers_in_srt(self) -> None:
        """
            Converts numbers in an SRT subtitle file to their word equivalents in Polish.
        """
        srt_file_path: str = path.join(
            self.working_space_temp_main_subs, self.filename)

        subs = load(srt_file_path, encoding='utf-8')

        number_in_words = NumberInWords()
        for i, sub in enumerate(subs):
            try:
                sub.text = number_in_words.convert_numbers_in_text(sub.text)
            except IndexError:
                console.print(
                    f"[red_bold]Wystąpił błąd w napisie {i+1}:[/red_bold] {sub.text}.\n[red_bold]Pomijam ten napis.", style='white_bold')

        subs.save(srt_file_path)

        console.print(
            "\nPrzekonwertowano liczby na słowa:", style='green_bold')
        console.print(srt_file_path, '\n', style='white_bold')

    def srt_to_ass(self) -> None:
        """
            This method updates the subtitles in an existing ASS file using the translated subtitles from an SRT file.
            If the ASS file does not exist, the SRT file is moved to the output directory.
            After these operations, the original ASS and SRT files are deleted.
        """
        srt_file_path: str = path.join(
            self.working_space_temp_alt_subs, self.filename)
        ass_file_path: str = path.join(
            self.working_space_temp_alt_subs, self.filename.replace('.srt', '.ass'))
        output_file_path: str = path.join(
            self.working_space_output, self.filename.replace('.srt', '.ass'))

        if stat(srt_file_path).st_size == 0:
            return

        srt_subs = load(srt_file_path, encoding='utf-8')

        if path.exists(ass_file_path):
            ass_subs = SSAFile.load(ass_file_path)
            srt_index = 0
            for event in ass_subs.events:
                if event.type == "Dialogue" and srt_index < len(srt_subs) and not re.search(r'\b(m|n) -?\d+', event.text):
                    # Sprawdź, czy tekst zawiera jakiekolwiek dekoratory
                    if re.search(r'{\\.*?}', event.text):
                        srt_index += 1
                        continue
                    srt_lines = srt_subs[srt_index].text.split('\n')
                    last_brace_position = event.text.rfind('}')
                    if last_brace_position != -1:
                        event.text = event.text[:last_brace_position +
                                                1] + '\n'.join(srt_lines)
                    else:
                        event.text = '\n'.join(srt_lines)
                    srt_index += 1
            ass_subs.save(output_file_path)
        else:
            srt_subs = load(srt_file_path, encoding='utf-8')
            ass_subs = SSAFile()
            for i, sub in enumerate(srt_subs):
                ass_subs.insert(i, SSAEvent(start=sub.start,
                                end=sub.end, text=sub.text))
            ass_subs.save(output_file_path)
            output_file_path = output_file_path.replace('.srt', '.ass')
            move(srt_file_path, output_file_path)

        console.print("Przeniesiono alternatywne napisy:", style="green_bold")
        console.print(output_file_path, style="white_bold")

        if path.exists(srt_file_path):
            remove(srt_file_path)
        if path.exists(ass_file_path):
            remove(ass_file_path)
