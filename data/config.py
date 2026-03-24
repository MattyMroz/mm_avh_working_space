"""
    This module provides the Config class.

    The Config class contains static methods to get the configuration options.
    These options include available translators, translation options, voice actors for text-to-speech, and output options.

    * Example usage:
        translators = Config.get_translators()
        translation_options = Config.get_translation_options()
        voice_actors = Config.get_voice_actors()
        output_options = Config.get_output()
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(slots=True)
class Config:
    """
    Config class contains static methods to get the configuration options.

    Methods:
        - get_translators() -> List[Dict[str, str]] - Returns a list of available translators.
        - get_translation_options() -> List[Dict[str, str]] - Returns a list of available translation options.
        - get_voice_actors() -> List[Dict[str, str]] - Returns a list of available voice actors for text-to-speech.
        - get_output() -> List[Dict[str, str]] - Returns a list of available output options.
    """

    @staticmethod
    def get_translators() -> List[Dict[str, str]]:
        """
        Returns a list of available translators.

        Each translator is represented as a dictionary with the following keys:
        - 'name': The name of the translator.
        - 'suboptions' (optional): A list of suboptions for the translator.

        Returns:
            List[Dict[str, str]]: A list of translators.
        """
        return [
            {'name': 'Google Translate'},
            {'name': 'DeepL API'},
            {'name': 'DeepL Desktop Free'},
            {
                'name': 'ChatGPT',
                'suboptions': [
                    {'name': 'ChatGPT + Google Translate'}
                ],
            },
        ]

    @staticmethod
    def get_translation_options() -> List[Dict[str, str]]:
        """
        Returns a list of available translation options.

        Each option is represented as a dictionary with the following key:
        - 'name': The name of the option.

        Returns:
            List[Dict[str, str]]: A list of translation options.
        """
        return [
            {'name': '10'},
            {'name': '20'},
            {'name': '30'},
            {'name': '40'},
            {'name': '50'},
            {'name': '60'},
            {'name': '70'},
            {'name': '80'},
            {'name': '90'},
            {'name': '100'},
        ]

    @staticmethod
    def get_voice_actors() -> List[Dict[str, str]]:
        """
        Returns a list of available voice actors for text-to-speech.

        Each voice actor is represented as a dictionary with the following keys:
        - 'name': The name of the voice actor.
        - 'description': A dictionary containing the description of the voice actor, including:
            - 'speed': The speed of the voice actor.
            - 'volume': The volume of the voice actor.
        - 'default_options': A dictionary containing the default options for the voice actor, including:
            - 'default_voice_speed': The default speed of the voice actor.
            - 'default_voice_volume': The default volume of the voice actor.

        Returns:
            List[Dict[str, str]]: A list of voice actors.
        """
        return [
            {
                'name': 'TTS - Zosia - Harpo',
                'description': {
                    'speed': 'Szybkość głosu od 0 do ... (słowa na minutę), domyślna: 200',
                    'volume': 'Głośność głosu od 0 do 1, domyślna: 0.7',
                },
                'default_options': {
                    'default_voice_speed': '200',
                    'default_voice_volume': '0.7',
                },
            },
            {
                'name': 'TTS - Agnieszka - Ivona',
                'description': {
                    'speed': 'Szybkość głosu od -10 do 10, domyślna: 5',
                    'volume': 'Głośność głosu od 0 do 100, domyślna: 65',
                },
                'default_options': {
                    'default_voice_speed': '5',
                    'default_voice_volume': '65',
                },
            },
            {
                'name': 'TTS - Zofia - Edge',
                'description': {
                    'speed': 'Szybkość głosu (+/- ? %) od -100% do +100%, domyślna: +40%',
                    'volume': 'Głośność głosu (+/- ? %) od -100% do +100%, domyślna: +0%',
                },
                'default_options': {
                    'default_voice_speed': '+40%',
                    'default_voice_volume': '+0%',
                },
            },
            {
                'name': 'TTS - Marek - Edge',
                'description': {
                    'speed': 'Szybkość głosu (+/- ? %) od -100% do +100%, domyślna: +40%',
                    'volume': 'Głośność głosu (+/- ? %) od -100% do +100%, domyślna: +0%',
                },
                'default_options': {
                    'default_voice_speed': '+40%',
                    'default_voice_volume': '+0%',
                },
            },
            {
                'name': 'TTS - *Głos* - ElevenLans',
                'description': {
                    'speed': 'Szybkość głosu: Auto',
                    'volume': 'Głośność głou: Auto',
                },
                'default_options': {
                    'default_voice_speed': 'auto',
                    'default_voice_volume': 'auto',
                },
            },
            {
                'name': 'TTS - STylish - PL',
                'description': {
                    'speed': 'Szybkość głosu od 0.5 do 2.0, domyślna: 1.0',
                    'volume': 'Głośność głosu: Auto',
                },
                'default_options': {
                    'default_voice_speed': '1.0',
                    'default_voice_volume': 'auto',
                },
            },
            {
                'name': 'TTS - Fish Audio API',
                'description': {
                    'speed': 'Szybkość głosu: Auto (kontrolowana przez temperature)',
                    'volume': 'Głośność głosu: Auto',
                },
                'default_options': {
                    'default_voice_speed': 'auto',
                    'default_voice_volume': 'auto',
                },
            },
            {
                'name': 'TTS - ReadLover API',
                'description': {
                    'speed': 'Szybkość głosu (length_scale) od 0.1 do 4.0, domyślna: 1.0',
                    'volume': 'Głośność głosu: Auto',
                },
                'default_options': {
                    'default_voice_speed': '1.0',
                    'default_voice_volume': 'auto',
                },
            },
            {
                'name': 'TTS - ElevenBytes',
                'description': {
                    'speed': 'Szybkość głosu: Auto',
                    'volume': 'Głośność głosu: Auto',
                },
                'default_options': {
                    'default_voice_speed': 'auto',
                    'default_voice_volume': 'auto',
                },
            },
        ]

    @staticmethod
    def get_post_processing() -> Dict[str, str]:
        """Returns post-processing configuration for FFmpeg speed/volume adjustment.

        These settings are independent of any TTS model and are applied
        AFTER the TTS engine generates the audio file.

        Returns:
            Dict with keys: description_speed, description_volume,
            default_pp_speed, default_pp_volume.
        """
        return {
            'description_speed': 'Przyspieszenie lektora (atempo) od 0.5 do 3.0, domyślna: 1.0 (bez zmiany)',
            'description_volume': 'Zmiana głośności lektora w dB (np. 0, 5, -3), domyślna: 0 (bez zmiany)',
            'default_pp_speed': '1.0',
            'default_pp_volume': '0',
        }

    @staticmethod
    def get_output() -> List[Dict[str, str]]:
        """
        Returns a list of available output options.

        Each option is represented as a dictionary with the following key:
        - 'name': The name of the output option.

        Returns:
            List[Dict[str, str]]: A list of output options.
        """
        return [
            {'name': 'Oglądam w MM_AVH_Players (wynik: napisy i audio)'},
            {'name': 'Scal do mkv'},
            {'name': 'Wypal do mp4'},
        ]
