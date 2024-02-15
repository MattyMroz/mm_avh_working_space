"""
    The MkvToolNix module provides a class for manipulating MKV files. It uses tools from the MKVToolNix package such as mkvextract, mkvmerge, and mkvinfo.

    * Example usage:
        mkvtoolnix = MkvToolNix(filename='example.mkv')
        mkv_info = mkvtoolnix.get_mkv_info()
        mkvtoolnix.mkv_extract_track(mkv_info)

    * Example output from get_mkv_info():
        {
            "container": {...},
            "global_tags": [...],
            "tracks": [...],
            "chapters": [...],
            "attachments": [...]
        }
"""

import sys
from subprocess import Popen, PIPE, CalledProcessError
from json import loads
from typing import Dict, List, Set
from os import path
from dataclasses import dataclass

from constants import (WORKING_SPACE,
                       WORKING_SPACE_OUTPUT,
                       WORKING_SPACE_TEMP,
                       MKV_EXTRACT_PATH,
                       MKV_MERGE_PATH, MKV_INFO_PATH,
                       MKV_PROPEDIT_PATH,
                       console)


@dataclass(slots=True)
class MkvToolNix:
    """
        A class for manipulating MKV files using the MKVToolNix package.

        Attributes:
            - filename (str): The name of the MKV file to be processed.
            - working_space (str): The directory where the MKV file is located.
            - working_space_output (str): The directory where the output files will be saved.
            - working_space_temp (str): The directory where temporary files will be saved during processing.
            - mkv_extract_path (str): The path to the mkvextract executable.
            - mkv_merge_path (str): The path to the mkvmerge executable.
            - mkv_info_path (str): The path to the mkvinfo executable.
            - mkv_propedit_path (str): The path to the mkvpropedit executable.

        Methods:
            - get_mkv_info(): Retrieves information about the MKV file using the mkvinfo tool.
            - mkv_extract_track(data: Dict[str, any]): Extracts the specified tracks from the MKV file using the mkvextract tool.
    """
    filename: str
    working_space: str = WORKING_SPACE
    working_space_output: str = WORKING_SPACE_OUTPUT
    working_space_temp: str = WORKING_SPACE_TEMP

    mkv_extract_path: str = MKV_EXTRACT_PATH
    mkv_merge_path: str = MKV_MERGE_PATH
    mkv_info_path: str = MKV_INFO_PATH
    mkv_propedit_path: str = MKV_PROPEDIT_PATH

    def _check_executables(self) -> None:
        """
            Checks if the MKVToolNix executables exist at the specified paths.
            If any executable is not found, the program will exit with an error message.
        """
        executables: List[str] = [self.mkv_extract_path,
                                  self.mkv_merge_path, self.mkv_info_path]
        for executable in executables:
            if not path.exists(executable):
                console.print(
                    f'Error: {executable} not found.', style='red_bold')
                sys.exit()

    def get_mkv_info(self) -> dict:
        """
            Retrieves information about the MKV file using the mkvinfo tool.
            The information is returned as a dictionary and also printed to the console.
            If an error occurs during the process, the program will exit with an error message.

            Returns:
            - dict: A dictionary containing information about the MKV file.
        """
        try:
            self._check_executables()
            command: List[str] = self._get_mkv_info_command()
            with Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, encoding='UTF-8') as process:
                output, error = process.communicate()

                if process.returncode == 0:
                    data: dict = loads(output)
                    tracks_data: List[dict] = self._parse_tracks_data(data)
                    self._print_mkv_info(tracks_data)
                    return data

                console.print(f'Error: {error}', style='red_bold')
        except (FileNotFoundError, CalledProcessError) as error:
            console.print(f'Error: {error}', style='red_bold')
            sys.exit()
        return {}

    def _get_mkv_info_command(self) -> List[str]:
        """
            Constructs the command to be used for retrieving information about the MKV file with mkvinfo.

            Returns:
                - List[str]: A list of strings representing the command to be executed.
        """
        return [
            self.mkv_merge_path,
            '--ui-language',
            'en',
            '--identify',
            '--identification-format',
            'json',
            path.join(self.working_space, self.filename)
        ]

    def _parse_tracks_data(self, data: dict) -> List[dict]:
        """
            Parses the track data from the dictionary returned by mkvinfo.

            Args:
                - data (dict): A dictionary containing information about the MKV file.

            Returns:
                - List[dict]: A list of dictionaries, each representing a track in the MKV file.
        """
        tracks_data: List[dict] = []

        for track in data['tracks']:
            track_data: dict = self._parse_track_data(track)
            tracks_data.append(track_data)

        return sorted(tracks_data, key=lambda x: x['id'])

    def _parse_track_data(self, track: dict) -> dict:
        """
            Parses the data for a single track from the dictionary returned by mkvinfo.
            Returns a dictionary with the track's ID, type, codec ID, language, IETF language, and properties.

            Args:
                - track (dict): A dictionary containing information about a single track in the MKV file.

            Returns:
                - dict: A dictionary containing information about a single track in the MKV file.
        """
        properties = track['properties']
        track_data: dict = {
            'id': track['id'],
            'type': track['type'],
            'codec_id': properties.get('codec_id', ''),
            'language': properties.get('language', ''),
            'language_ietf': properties.get('language_ietf', ''),
            'properties': self._get_track_properties(properties)
        }

        return track_data

    @staticmethod
    def _get_track_properties(properties: dict) -> str:
        """
            Retrieves the properties of a track from the dictionary returned by mkvinfo.

            Args:
                - properties (dict): A dictionary containing the properties of a track in the MKV file.

            Returns:
                - str: A string containing the properties of a track in the MKV file.
        """
        if 'display_dimensions' in properties:
            return properties['display_dimensions']
        if 'audio_sampling_frequency' in properties:
            return f"{properties['audio_sampling_frequency']} Hz"
        return 'None'

    def _print_mkv_info(self, tracks_data: List[dict]) -> None:
        """
            Prints the information about the MKV file to the console.
            The information includes the ID, type, codec ID, language, IETF language, and properties of each track.

            Args:
                - tracks_data (List[dict]): A list of dictionaries, each representing a track in the MKV file.
        """
        console.print('WYODRĘBNIANIE Z PLIKU:',
                      style='yellow_bold')
        console.print(self.filename, style='white_bold')
        console.print('ID  TYPE        CODEK                LANG  LANG_IETF  PROPERTIES',
                      style='yellow_bold')

        for track in tracks_data:
            console.print(
                f'[yellow_bold]{track["id"]:2}[/yellow_bold]  '
                f'[white_bold]{track["type"]:10}  '
                f'{track["codec_id"]:20} '
                f'{track["language"]:5} '
                f'{track["language_ietf"]:10} '
                f'{track["properties"]}'
            )
        console.print()

    def mkv_extract_track(self, data: Dict[str, any]) -> None:
        """
            Extracts the specified tracks from the MKV file using the mkvextract tool.
            The tracks to be extracted are specified by their IDs.
            The user is prompted to enter the IDs of the tracks to be extracted.
            If an error occurs during the process, the program will exit with an error message.

            Args:
                - data (Dict[str, any]): A dictionary containing information about the MKV file.
        """
        valid_track_range: range = range(len(data['tracks']))
        tracks_to_extract: Set[int] = set()

        while True:
            try:
                console.print('Podaj ID ścieżki do wyciągnięcia (naciśnij ENTER, aby zakończyć): ',
                              style='green_bold', end='')
                track_input: str = input().strip()
                if not track_input:
                    break
                track_id: int = int(track_input)

                if track_id in valid_track_range:
                    tracks_to_extract.add(track_id)
                else:
                    console.print(
                        'Nieprawidłowy ID ścieżki. Proszę podać poprawny numer ścieżki.\n', style='red_bold')
            except ValueError:
                console.print(
                    'Pominięto wyciąganie ścieżki.\n', style='red_bold')

        try:
            for track_id in tracks_to_extract:
                track: str = data['tracks'][track_id]
                codec_id: str = track['properties']['codec_id']
                format_extension: str = self._get_format_extension(codec_id)
                filename: str = f'{self.filename[:-4]}.{format_extension}'
                out_file: str = path.join(self.working_space_temp, filename)
                command: List[str] = self._get_extract_command(
                    track_id, out_file)

                with Popen(command) as process:
                    console.print(
                        f'\nEkstrakcja ścieżki {track_id} do pliku {filename}', style='yellow_bold')
                    process.wait()

        except (IndexError, KeyError):
            console.print(
                'Znaleziono nieprawidłowe ID ścieżki!', style='red_bold')
            self.mkv_extract_track(data)

        console.print(
            'Ekstrakcja zakończona pomyślnie.\n', style='green_bold')

    @staticmethod
    def _get_format_extension(codec_id: str) -> str:
        """
            Determines the file extension for a track based on its codec ID.

            Args:
                - codec_id (str): The codec ID of a track in the MKV file.

            Returns:
                - str: The file extension for the track.
        """
        format_dict: dict = {
            'A_AAC/MPEG2/*': 'aac',
            'A_AAC/MPEG4/*': 'aac',
            'A_AAC': 'aac',
            'A_AC3': 'ac3',
            'A_EAC3': 'ac3',
            'A_ALAC': 'caf',
            'A_DTS': 'dts',
            'A_FLAC': 'flac',
            'A_MPEG/L2': 'mp2',
            'A_MPEG/L3': 'mp3',
            'A_OPUS': 'opus',
            'A_PCM/INT/LIT': 'wav',
            'A_PCM/INT/BIG': 'wav',
            'A_REAL/*': 'rm',
            'A_TRUEHD': 'truehd',
            'A_MLP': 'mlp',
            'A_TTA1': 'tta',
            'A_VORBIS': 'ogg',
            'A_WAVPACK4': 'wv',
            'S_HDMV/PGS': 'sup',
            'S_HDMV/TEXTST': 'txt',
            'S_KATE': 'ogg',
            'S_TEXT/SSA': 'ssa',
            'S_TEXT/ASS': 'ass',
            'S_SSA': 'ssa',
            'S_ASS': 'ass',
            'S_TEXT/UTF8': 'srt',
            'S_TEXT/ASCII': 'srt',
            'S_VOBSUB': 'sub',
            'S_TEXT/USF': 'usf',
            'S_TEXT/WEBVTT': 'vtt',
            'V_MPEG1': 'mpeg',
            'V_MPEG2': 'mpeg',
            'V_MPEG4/ISO/AVC': 'h264',
            'V_MPEG4/ISO/HEVC': 'h265',
            'V_MS/VFW/FOURCC': 'avi',
            'V_REAL/*': 'rm',
            'V_THEORA': 'ogg',
            'V_VP8': 'ivf',
            'V_VP9': 'ivf'
        }

        return format_dict.get(codec_id, 'mkv')

    def _get_extract_command(self, track_id: int, out_file: str) -> List[str]:
        """
            Constructs the command to be used for extracting a track from the MKV file with mkvextract.
            Returns the command as a list of strings.

            Args:
                - track_id (int): The ID of the track to be extracted.
                - out_file (str): The path and filename of the output file.

            Returns:
                - List[str]: The command to be used for extracting the track.
        """
        return [
            self.mkv_extract_path,
            'tracks',
            path.join(self.working_space, self.filename),
            f'{track_id}:{out_file}'
        ]
