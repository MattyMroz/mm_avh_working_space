"""
    This module defines the 'MKVProcessing' class, which processes MKV files.

    * Usage:
        To use this module, create an instance of the 'MKVProcessing' class and call the 'process_mkv' method.
    * Example: Frist create an instance of the MKVProcessing class:
        processor = MKVProcessing(filename="example.mkv",
                                crf_value="18",
                                preset_value="medium")
    * Example usage:
        processor.process_mkv(settings)
"""

import re
from contextlib import suppress
from dataclasses import dataclass
from os import listdir, path, remove, rename
from shutil import move
from subprocess import Popen, call
from typing import List, Dict, Callable, Optional

from constants import (WORKING_SPACE,
                       WORKING_SPACE_OUTPUT,
                       MKV_MERGE_PATH,
                       FFMPEG_PATH,
                       console)
from data.settings import Settings


@dataclass(slots=True)
class MKVProcessing:
    """
        The 'MKVProcessing' class is used for processing MKV files.

        Attributes:
            - filename (str): The name of the MKV file to process.
            - working_space (str): The path to the working directory.
            - working_space_output (str): The path to the output directory.
            - mkv_merge_path (str): The path to the MKVMerge executable.
            - ffmpeg_path (str): The path to the FFmpeg executable.
            - crf_value (str): The Constant Rate Factor value for FFmpeg.
            - preset_value (str): The preset value for FFmpeg.

        Methods:
            - process_mkv(self, settings: Settings) -> None:
                Processes the MKV file based on the specified settings.

            - move_files_to_working_space(self) -> None:
                Moves the processed files to the working directory.

            - mkv_merge(self) -> None:
                Merges the MKV file with the generated audio and subtitle files.

            - mkv_burn_to_mp4(self) -> None:
                Burns the subtitles into the MKV file and converts it to MP4.
    """
    filename: str
    working_space: str = WORKING_SPACE
    working_space_output: str = WORKING_SPACE_OUTPUT
    mkv_merge_path: str = MKV_MERGE_PATH
    ffmpeg_path: str = FFMPEG_PATH

    crf_value: str = '18'
    preset_value: str = 'ultrafast'

    def process_mkv(self, settings: Settings) -> None:
        """
            Processes the MKV file based on the specified settings.

            This method takes a Settings object as input and processes the MKV file accordingly. The processing options include moving the processed files to the working directory, merging the MKV file with the generated audio and subtitle files, and burning the subtitles into the MKV file and converting it to MP4.

            Args:
                settings (Settings): The settings for processing the MKV file.
        """
        options: Dict[str, Callable] = {
            'Oglądam w MM_AVH_Players (wynik: napisy i audio)': self.move_files_to_working_space,
            'Scal do mkv': self.mkv_merge,
            'Wypal do mp4': self.mkv_burn_to_mp4,
        }

        process_method: Optional[Callable] = options.get(settings.output)
        if process_method:
            console.print(
                f'\nRozpoczynam przetwarzane pliku o nazwie: {self.filename}...', style='green_bold')
            process_method()
            console.print(
                f'\nZakończono i zapisano plik o nazwie: {self.filename}... w odpowiednim folderze.', style='green_bold')

    def move_files_to_working_space(self) -> None:
        """
        Moves the processed files to the working directory.

        This method iterates over the files in the output directory and moves any files that start with the filename of the MKV file being processed to the working directory.
        """
        for filename in listdir(self.working_space_output):
            if filename.startswith(self.filename):
                destination_path = path.join(self.working_space, filename)
                if path.exists(destination_path):
                    remove(destination_path)
                move(path.join(self.working_space_output, filename), destination_path)

    def mkv_merge(self) -> None:
        """
            Merges the MKV file with the generated audio and subtitle files.

            This method takes the MKV file and merges it with the generated audio and subtitle files using the MKVMerge tool. The merged file is then saved in the output directory.
        """
        input_file: str = path.join(self.working_space, self.filename + '.mkv')
        if not path.exists(input_file):
            console.print(
                f'[red_bold]Plik {input_file} nie istnieje. Pomijam...')
            return
        output_file: str = path.join(
            self.working_space_output, self.filename + '.mkv')

        subtitle_file_srt: str = path.join(
            self.working_space_output, self.filename + '.srt')
        subtitle_file_ass: str = path.join(
            self.working_space_output, self.filename + '.ass')
        lector_file: str = path.join(
            self.working_space_output, self.filename + '.eac3')

        command: List[str] = [self.mkv_merge_path,
                              '-o', output_file, input_file]
        if path.exists(lector_file):
            command.extend(['--language', '0:pol', '--track-name',
                           '0:Lektor PL', '--default-track', '0:no', lector_file])
        if path.exists(subtitle_file_srt):
            command.extend(['--language', '0:pol', '--track-name',
                           '0:Napisy Poboczne PL', '--default-track', '0:no', subtitle_file_srt])
        elif path.exists(subtitle_file_ass):
            command.extend(['--language', '0:pol', '--track-name',
                           '0:Napisy Poboczne PL', '--default-track', '0:no', subtitle_file_ass])

        process = Popen(command)
        process.communicate()

        self._remove_files([subtitle_file_srt, subtitle_file_ass, lector_file])

    def mkv_burn_to_mp4(self) -> None:
        """
            Burns the subtitles into the MKV file and converts it to MP4.

            This method takes the MKV file, burns the subtitles into the video, and converts the file to MP4 format using FFmpeg. The converted file is then saved in the output directory.
        """
        filename: str = self.filename + '.mkv'
        if not path.exists(path.join(self.working_space, filename)):
            console.print(
                f'Plik {filename} nie istnieje w {self.working_space}. Pomijam...', style='red_bold')
            return
        new_filename: str = re.sub(r'[^A-Za-z0-9.]+', '_', filename)

        rename(path.join(self.working_space, filename),
               path.join(self.working_space, new_filename))

        subtitle_file_srt: str = path.join(
            self.working_space_output, self.filename + '.srt')
        subtitle_file_ass: str = path.join(
            self.working_space_output, self.filename + '.ass')
        lector_file: str = path.join(
            self.working_space_output, self.filename + '.eac3')

        output_file: str = path.join(
            self.working_space_output, new_filename[:-4] + '.mp4')

        command: List[str] = self._prepare_command(
            new_filename, output_file, lector_file, subtitle_file_srt, subtitle_file_ass)

        with suppress(Exception):
            call(command)

        if path.exists(output_file):
            target_file = path.join(
                self.working_space_output, filename[:-4] + '.mp4')
            if path.exists(target_file) and output_file != target_file:
                remove(target_file)
            rename(output_file, target_file)

        rename(path.join(self.working_space, new_filename),
               path.join(self.working_space, filename))

        self._remove_files([subtitle_file_srt, subtitle_file_ass, lector_file])

    def _remove_files(self, files: List[str]) -> None:
        """
            Removes the specified files.

            This method takes a list of file paths and removes each file if it exists.

            Args:
                files (List[str]): The list of files to remove.
        """
        for file in files:
            if path.exists(file):
                remove(file)

    def _prepare_command(self, new_filename: str, output_file: str, lector_file: str, subtitle_file_srt: str, subtitle_file_ass: str) -> List[str]:
        """
            Prepares the FFmpeg command for burning the subtitles and converting the file.

            This method takes the paths to the new filename, output file, lector file, and subtitle files, and prepares the FFmpeg command for burning the subtitles into the video and converting the file to MP4 format.

            Args:
                new_filename (str): The new filename for the MKV file.
                output_file (str): The path to the output file.
                lector_file (str): The path to the lector file.
                subtitle_file_srt (str): The path to the SRT subtitle file.
                subtitle_file_ass (str): The path to the ASS subtitle file.

            Returns:
                List[str]: The prepared FFmpeg command.
        """
        command: List[str] = []

        if (path.exists(subtitle_file_srt) or path.exists(subtitle_file_ass)) and path.exists(lector_file):
            command = [self.ffmpeg_path, '-y', '-i', path.join(self.working_space, new_filename), '-i', lector_file.replace("\\", "/")[
                2:], '-c:v', 'libx264', '-crf', self.crf_value, '-preset', self.preset_value, '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0']

            if path.exists(subtitle_file_srt):
                command.extend(
                    ['-vf', 'subtitles=' + subtitle_file_srt.replace("\\", "/")[2:]])
            elif path.exists(subtitle_file_ass):
                command.extend(
                    ['-vf', 'subtitles=' + subtitle_file_ass.replace("\\", "/")[2:]])

        elif path.exists(lector_file):
            command = [self.ffmpeg_path, '-y', '-i', path.join(self.working_space, new_filename), '-i', lector_file.replace(
                "\\", "/")[2:], '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0']

        elif path.exists(subtitle_file_srt) or path.exists(subtitle_file_ass):
            command = [self.ffmpeg_path, '-y', '-i', path.join(self.working_space, new_filename),
                       '-c:v', 'libx264', '-crf', self.crf_value, '-preset', self.preset_value, '-c:a', 'copy']

            if path.exists(subtitle_file_srt):
                command.extend(
                    ['-vf', 'subtitles=' + subtitle_file_srt.replace("\\", "/")[2:]])
            elif path.exists(subtitle_file_ass):
                command.extend(
                    ['-vf', 'subtitles=' + subtitle_file_ass.replace("\\", "/")[2:]])

        command.append(output_file.replace("\\", "/")[2:])

        return command
