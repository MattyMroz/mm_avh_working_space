"""
    Module `Settings` provides a versatile configuration management system
        for your application.
    It includes a `Settings` class that allows users to customize various options
        and save them to a JSON file.

    * Example: First, create an instance of the `Settings` class:
        settings = Settings()

    * Example usage of the `Settings` class:
        settings.change_settings_save_to_file('settings.json')
        - If the file doesn't exist, it will be created with default settings.
        - If the file exists, it will be overwritten with the current settings.
        - If the file exists with incomplete settings, missing settings will be added with default values.

    * Example default settings in 'settings.json':
        {
        "translator": "Google Translator",
        "deepl_api_key": "null",
        "translated_line_count": "50",
        "tts": "TTS - Agnieszka - Ivona",
        "tts_speed": "5",
        "tts_volume": "65",
        "output": "Ogl\u0105dam w MM_AVH_Players (wynik: napisy i audio)"
        }
"""

from dataclasses import asdict, dataclass
from json import decoder, dump, load
from typing import Any, Dict, List, Optional, Tuple

from constants import SETTINGS_PATH, console
from data.config import Config


@dataclass(slots=True)
class Settings:
    """
        A class representing application settings.

        Attributes:
            - translator (Optional[str]): The selected translator.
            - deepl_api_key (Optional[str]): The API key for DeepL translation service.
            - translated_line_count (Optional[str]): The number of translated lines.
            - tts (Optional[str]): The selected TTS engine.
            - tts_speed (Optional[str]): The speed of the TTS voice.
            - tts_volume (Optional[str]): The volume of the TTS voice.
            - output (Optional[str]): The selected output option.
            - auto_mode (bool): When True, the pipeline runs unattended (tracks,
                styles, translation and audio are decided automatically and
                logged, with no Y/N prompts). Defaults to False.

        Methods:
            - load_from_file(cls, settings_path: str) -> 'Settings': Load settings from a file.
            - _set_option(prompt: str, options: List[Dict[str, Any]]) -> Optional[str]: Set an option from a list of options.
            - _is_valid_speed(speed: str, tts: Optional[str]) -> bool: Check if a given speed value is valid for the selected TTS engine.
            - _is_valid_volume(volume: str, tts: Optional[str]) -> bool: Check if a given volume value is valid for the selected TTS engine.
            - _get_translator(settings: Optional['Settings']) -> Optional[str]: Get the selected translator.
            - _get_deepl_api_key(settings: Optional['Settings']) -> Optional[str]: Get the DeepL API key.
            - _get_translated_line_count(settings: Optional['Settings']) -> Optional[str]: Get the number of translated lines.
            - _get_tts(settings: Optional['Settings']) -> Optional[str]: Get the selected TTS engine.
            - _get_default_speed_volume(tts: Optional[str]) -> Tuple[Optional[str], Optional[str]]: Get the default speed and volume for a TTS engine.
            - _get_tts_speed(tts: Optional[str], default_speed: Optional[str]) -> Optional[str]: Get the TTS speed.
            - _get_tts_volume(tts: Optional[str], default_volume: Optional[str]) -> Optional[str]: Get the TTS volume.
            - _get_output(settings: Optional['Settings']) -> Optional[str]: Get the selected output option.
            - get_user_settings(settings_path: str) -> Optional['Settings']: Get user settings from a file.
            - change_settings_save_to_file(settings_path: str) -> None: Change and save settings to a file.
    """
    translator: Optional[str] = None
    deepl_api_key: Optional[str] = None
    translated_line_count: Optional[str] = None
    tts: Optional[str] = None
    tts_speed: Optional[str] = None
    tts_volume: Optional[str] = None
    elevenbytes_voice: Optional[str] = None
    elevenbytes_stability: Optional[str] = None
    elevenbytes_similarity_boost: Optional[str] = None
    elevenbytes_style: Optional[str] = None
    elevenbytes_speaker_boost: Optional[str] = None
    pp_speed: Optional[str] = None
    pp_volume: Optional[str] = None
    output: Optional[str] = None
    auto_mode: bool = False

    @classmethod
    def load_from_file(cls, settings_path: str = SETTINGS_PATH) -> 'Settings':
        """
            Load settings from a JSON file.

            Args:
                - settings_path (str): The name of the file to load settings from.

            Returns:
                - Settings: An instance of the Settings class with the loaded settings.

            Raises:
                - FileNotFoundError: If the file does not exist.
                - decoder.JSONDecodeError: If the file has an invalid JSON format.
        """

        def get_default_settings():
            return cls(
                translator='Google Translator',
                deepl_api_key=None,
                translated_line_count='50',
                tts='TTS - Agnieszka - Ivona',
                tts_speed='5',
                tts_volume='65',
                pp_speed='1.0',
                pp_volume='0',
                output='Oglądam w MM_AVH_Players (wynik: napisy i audio)'
            )

        try:
            with open(settings_path, 'r', encoding='utf-8') as file:
                data = load(file)
        except FileNotFoundError:
            console.print(
                f'Nie znaleziono pliku {settings_path}', style='red_bold')
            console.print('Musisz najpierw ustawić ustawienia.',
                          style='red_bold')
            return get_default_settings()

        except decoder.JSONDecodeError:
            console.print(
                f'Niepoprawny format pliku {settings_path}', style='red_bold')
            return get_default_settings()

        pp_defaults = Config.get_post_processing()
        return Settings(
            translator=data.get('translator'),
            deepl_api_key=data.get('deepl_api_key'),
            translated_line_count=data.get('translated_line_count'),
            tts=data.get('tts'),
            tts_speed=data.get('tts_speed'),
            tts_volume=data.get('tts_volume'),
            elevenbytes_voice=data.get('elevenbytes_voice'),
            elevenbytes_stability=data.get('elevenbytes_stability'),
            elevenbytes_similarity_boost=data.get('elevenbytes_similarity_boost'),
            elevenbytes_style=data.get('elevenbytes_style'),
            elevenbytes_speaker_boost=data.get('elevenbytes_speaker_boost'),
            pp_speed=data.get('pp_speed', pp_defaults['default_pp_speed']),
            pp_volume=data.get('pp_volume', pp_defaults['default_pp_volume']),
            output=data.get('output'),
            auto_mode=data.get('auto_mode', False)
        )

    @staticmethod
    def _set_option(prompt: str, options: List[Dict[str, Any]]) -> Optional[str]:
        """
            Set an option from a list of options.

            Args:
                - prompt (str): The prompt to display to the user.
                - options (List[Dict[str, Any]]): The list of options to choose from.

            Returns:
                - Optional[str]: The selected option, or None if the selection is invalid.
        """
        console.print(f'\n{prompt}', style='yellow_bold')
        for i, option in enumerate(options):
            console.print(
                f'[yellow_bold]{i + 1}.[/yellow_bold] [white]{option["name"]}')
            if 'suboptions' in option:
                for j, suboption in enumerate(option['suboptions']):
                    console.print(
                        f'[yellow_bold]    {i + 1}.{j + 1}.[/yellow_bold] [white]{suboption["name"]}')
            elif 'description' in option:
                console.print(
                    f'    [white]{option["description"]["speed"]}')
                console.print(
                    f'    [white]{option["description"]["volume"]}')
        console.print('Wybierz opcję: ', style='green_bold', end='')
        choice = input()
        if '.' in choice:
            major_choice, minor_choice = map(int, choice.split('.'))
            if 1 <= major_choice <= len(options) and 1 <= minor_choice <= len(options[major_choice - 1]['suboptions']):
                return options[major_choice - 1]['suboptions'][minor_choice - 1]['name']
        elif choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]['name']
        else:
            for option in options:
                if option['name'] == choice:
                    return option['name']
        console.print(
            'Niepoprawny wybór. Nie zmieniono wartości!', style='red_bold')
        return None

    @staticmethod
    def _is_valid_speed(speed: str, tts: Optional[str]) -> bool:
        """
            Check if a given speed value is valid for the selected TTS engine.

            Args:
                - speed (str): The speed value to check.
                - tts (Optional[str]): The selected TTS engine.

            Returns:
                - bool: True if the speed value is valid, False otherwise.
        """
        if tts == 'TTS - Zosia - Harpo':
            return int(speed) >= 0
        if tts == 'TTS - Agnieszka - Ivona':
            return -10 <= int(speed) <= 10
        if tts in {'TTS - Zofia - Edge', 'TTS - Marek - Edge'}:
            return speed.startswith(('+', '-')) and speed[1:-1].isdigit() and -100 <= int(
                speed[1:-1]) <= 100 and speed.endswith('%')
        return False

    @staticmethod
    def _is_valid_volume(volume: str, tts: Optional[str]) -> bool:
        """
            Check if a given volume value is valid for the selected TTS engine.

            Args:
                - volume (str): The volume value to check.
                - tts (Optional[str]): The selected TTS engine.

            Returns:
                - bool: True if the volume value is valid, False otherwise.
        """
        if tts == 'TTS - Zosia - Harpo':
            return 0 <= float(volume) <= 1
        if tts == 'TTS - Agnieszka - Ivona':
            return -100 <= int(volume) <= 100
        if tts in {'TTS - Zofia - Edge', 'TTS - Marek - Edge'}:
            return volume.startswith(('+', '-')) and volume[1:-1].isdigit() and -100 <= int(
                volume[1:-1]) <= 100 and volume.endswith('%')
        return False

    @staticmethod
    def _get_translator(settings: Optional['Settings']) -> Optional[str]:
        """
            Retrieve the selected translator from the user settings or prompt the user to choose one.

            Args:
                - settings (Optional['Settings']): The user settings object.

            Returns:
                - Optional[str]: The selected translator or None if not found.
        """

        translator = Settings._set_option(
            'Wybierz tłumacza: ', Config.get_translators())
        if translator is None:
            translator = settings.translator if settings else None
        return translator

    @staticmethod
    def _get_deepl_api_key(settings: Optional['Settings']) -> Optional[str]:
        """
            Prompt the user to set the DeepL API key or retrieve it from the user settings.

            Args:
                - settings (Optional['Settings']): The user settings object.

            Returns:
                - Optional[str]: The DeepL API key or None if not set.
        """

        console.print(
            '\nCzy chcesz ustawić klucz API DeepL?', style="yellow_bold")
        console.print('(T lub Y - tak): ', style='green_bold', end='')
        if input().lower() in ('t', 'y'):
            console.print(
                'Klucz API DeepL można wygenerować na stronie https://www.deepl.com/pro-api', style='yellow_bold')
            console.print('Podaj klucz API DeepL: ',
                          style='green_bold', end='')
            deepl_api_key: Optional[str] = input('')
            if deepl_api_key == '':
                deepl_api_key = settings.deepl_api_key if settings else None
                console.print(
                    'Niepoprawna wartość. Nie zmieniono wartości!', style='red_bold')
        else:
            deepl_api_key = settings.deepl_api_key if settings else None
        return deepl_api_key

    @staticmethod
    def _get_translated_line_count(settings: Optional['Settings']) -> Optional[str]:
        """
            Prompt the user to set the number of translated lines or retrieve it from the user settings.

            Args:
                - settings (Optional['Settings']): The user settings object.

            Returns:
                - Optional[str]: The number of translated lines or None if not set. (Optional[str] future maybe change)
        """

        translated_line_count = Settings._set_option('Wybierz liczbę przetłumaczonych linii: ',
                                                     Config.get_translation_options())
        if translated_line_count is None:
            translated_line_count = settings.translated_line_count if settings else None
        return translated_line_count

    @staticmethod
    def _get_tts(settings: Optional['Settings']) -> Optional[str]:
        """
            Prompt the user to choose a TTS engine or retrieve it from the user settings.

            Args:
                - settings (Optional['Settings']): The user settings object.

            Returns:
                - Optional[str]: The selected TTS engine or None if not set.
        """

        tts = Settings._set_option(
            'Wybierz silnik TTS: ', Config.get_voice_actors())
        if tts is None:
            tts = settings.tts if settings else None
        return tts

    @staticmethod
    def _get_default_speed_volume(tts: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
            Retrieve the default voice speed and volume for the specified TTS engine.

            Args:
                - tts (Optional[str]): The selected TTS engine.

            Returns:
                - Tuple[Optional[str], Optional[str]]: A tuple containing the default voice speed and volume,
                    or (None, None) if not found.
        """

        default_speed = None
        default_volume = None
        voice_actor = next(
            (actor for actor in Config.get_voice_actors() if actor['name'] == tts), None)
        if voice_actor:
            default_speed = voice_actor['default_options']['default_voice_speed']
            default_volume = voice_actor['default_options']['default_voice_volume']
        return default_speed, default_volume

    @staticmethod
    def _get_tts_speed(tts: Optional[str], default_speed: Optional[str]) -> Optional[str]:
        """
            Prompt the user to enter the voice speed for the selected TTS engine, or use the default speed.

            Args:
                - tts (Optional[str]): The selected TTS engine.
                - default_speed (Optional[str]): The default voice speed for the TTS engine.

            Returns:
                - Optional[str]: The selected voice speed or the default speed if not set.
        """

        console.print('Wpisz szybkość głosu: ', style='green_bold', end='')
        tts_speed_choice = input()
        try:
            tts_speed = tts_speed_choice if (
                Settings._is_valid_speed(
                    tts_speed_choice, tts) and tts_speed_choice.strip() != ''
            ) else default_speed
        except ValueError:
            console.print(
                'Niepoprawna wartość szybkości. Używam domyślnej wartości.', style='red_bold')
            tts_speed = default_speed
        return tts_speed

    @staticmethod
    def _get_tts_volume(tts: Optional[str], default_volume: Optional[str]) -> Optional[str]:
        """
            Prompt the user to enter the voice volume for the selected TTS engine, or use the default volume.

            Args:
                - tts (Optional[str]): The selected TTS engine.
                - default_volume (Optional[str]): The default voice volume for the TTS engine.

            Returns:
                - Optional[str]: The selected voice volume or the default volume if not set.
        """

        console.print('Wpisz głośność głosu: ',
                      style='green_bold', end='')
        tts_volume_choice = input()
        try:
            tts_volume = tts_volume_choice if (
                Settings._is_valid_volume(
                    tts_volume_choice, tts) and tts_volume_choice.strip() != ''
            ) else default_volume
        except ValueError:
            console.print(
                'Niepoprawna wartość głośności. Używam domyślnej wartości.', style='red_bold')
            tts_volume = default_volume
        return tts_volume

    @staticmethod
    def _get_elevenbytes_voice(settings: Optional['Settings']) -> Optional[str]:
        """Fetch available voices from ElevenBytes and let user choose or add custom."""
        try:
            from modules.tts_elevenbytes import TTS as ElevenBytesTTS
        except Exception as exc:
            console.print(
                f'\n[red_bold]Nie można zaimportować ElevenBytes: {exc}')
            return settings.elevenbytes_voice if settings else None

        voices = ElevenBytesTTS.list_voices()
        voice_list = list(voices.items())

        console.print('\n[yellow_bold]Dostępne głosy ElevenBytes (ElevenLabs):')
        for i, (alias, (name, voice_id)) in enumerate(voice_list):
            console.print(
                f'[yellow_bold]{i + 1}.[/yellow_bold] [white]{name} ({alias})')
        add_idx = len(voice_list) + 1
        console.print(
            f'[yellow_bold]{add_idx}.[/yellow_bold] [white]➕ Dodaj nowy głos (voice_id z ElevenLabs)')
        console.print('Wybierz głos: ', style='green_bold', end='')
        choice = input().strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(voice_list):
                alias = voice_list[idx][0]
                console.print(
                    f'Wybrano głos: {voice_list[idx][1][0]}', style='yellow_bold')
                return alias
            if int(choice) == add_idx:
                console.print(
                    'Podaj voice_id z ElevenLabs: ', style='green_bold', end='')
                voice_id = input().strip()
                if not voice_id:
                    console.print(
                        'Pusty voice_id. Nie zmieniono wartości!', style='red_bold')
                    return settings.elevenbytes_voice if settings else None
                console.print(
                    'Podaj nazwę głosu (np. "Rachel — Calm"): ', style='green_bold', end='')
                voice_name = input().strip() or f'Custom ({voice_id[:8]}...)'
                alias = voice_id
                ElevenBytesTTS.add_voice(alias, voice_name, voice_id)
                console.print(
                    f'Dodano i wybrano głos: {voice_name}', style='yellow_bold')
                return alias

        console.print(
            'Niepoprawny wybór. Nie zmieniono wartości!', style='red_bold')
        return settings.elevenbytes_voice if settings else None

    @staticmethod
    def _prompt_float_0_1(description: str, verb: str, current: str, default: str) -> str:
        """Ask for a 0.0–1.0 value in the project's prompt style.

        Args:
            description: Full Polish label, e.g. 'Stabilność głosu'.
            verb: Short noun for the 'Wpisz ...:' line, e.g. 'stabilność'.
            current: Currently saved value shown to the user; kept on empty input.
            default: Factory default value shown alongside the current one.
        """
        console.print(f'\n{description} (0.0-1.0)')
        console.print(f'(obecna: {current}, domyślna: {default}, Enter = bez zmiany)')
        console.print(f'Wpisz {verb}: ', style='green_bold', end='')
        choice = input().strip()
        if not choice:
            return current
        try:
            val = float(choice)
            if 0.0 <= val <= 1.0:
                return choice
        except ValueError:
            pass
        console.print('Niepoprawna wartość. Używam domyślnej wartości.', style='red_bold')
        return default

    # Fabryczne domyślne voice_settings ElevenLabs v3 (bezpieczne dla modelu).
    _V3_DEFAULT_STABILITY = '0.5'
    _V3_DEFAULT_SIMILARITY = '0.75'
    _V3_DEFAULT_STYLE = '0.0'
    _V3_DEFAULT_BOOST = 'true'

    @staticmethod
    def _get_elevenbytes_v3_settings(
        settings: Optional['Settings'],
    ) -> tuple[str, str, str, str]:
        """Prompt user for ElevenLabs v3 voice_settings (stability, similarity_boost, style, speaker_boost).

        Enter on any field keeps the currently saved value; the factory default is
        shown alongside. Returns the four values as strings, ready to persist.
        """
        prev = settings if settings else None
        cur_stability = (prev.elevenbytes_stability if prev and prev.elevenbytes_stability else Settings._V3_DEFAULT_STABILITY)
        cur_similarity = (prev.elevenbytes_similarity_boost if prev and prev.elevenbytes_similarity_boost else Settings._V3_DEFAULT_SIMILARITY)
        cur_style = (prev.elevenbytes_style if prev and prev.elevenbytes_style else Settings._V3_DEFAULT_STYLE)
        cur_boost = (prev.elevenbytes_speaker_boost if prev and prev.elevenbytes_speaker_boost else Settings._V3_DEFAULT_BOOST)

        console.print('\n[yellow_bold]Ustawienia głosu ElevenLabs v3 (Enter = bez zmiany):')
        stability = Settings._prompt_float_0_1('Stabilność głosu', 'stabilność', cur_stability, Settings._V3_DEFAULT_STABILITY)
        similarity_boost = Settings._prompt_float_0_1('Podobieństwo do głosu', 'podobieństwo', cur_similarity, Settings._V3_DEFAULT_SIMILARITY)
        style = Settings._prompt_float_0_1('Ekspresja stylu', 'ekspresję', cur_style, Settings._V3_DEFAULT_STYLE)

        cur_boost_label = 'tak' if cur_boost == 'true' else 'nie'
        def_boost_label = 'tak' if Settings._V3_DEFAULT_BOOST == 'true' else 'nie'
        console.print('\nWzmocnienie mówcy — wierność brzmienia (T/N)')
        console.print(f'(obecne: {cur_boost_label}, domyślne: {def_boost_label}, Enter = bez zmiany)')
        console.print('Włączyć wzmocnienie mówcy? (T/N): ', style='green_bold', end='')
        boost_choice = input().strip().lower()
        if boost_choice in ('t', 'y', 'true'):
            speaker_boost = 'true'
        elif boost_choice in ('n', 'false'):
            speaker_boost = 'false'
        else:
            speaker_boost = cur_boost

        return stability, similarity_boost, style, speaker_boost

    @staticmethod
    def _get_auto_mode(settings: Optional['Settings']) -> bool:
        """Prompt user to toggle unattended auto mode (T/N). Enter keeps current value."""
        current = settings.auto_mode if settings else False
        current_label = 'tak' if current else 'nie'
        console.print(
            f'\nTryb automatyczny — pipeline bez pytań poza tym menu (T/N), '
            f'obecnie: {current_label}')
        console.print('Włączyć tryb automatyczny? (T/N): ',
                      style='green_bold', end='')
        choice = input().strip().lower()
        if choice in ('t', 'y'):
            return True
        if choice in ('n',):
            return False
        return current

    @staticmethod
    def _is_valid_pp_speed(speed: str) -> bool:
        """Check if post-processing speed value is valid (0.5-3.0)."""
        try:
            val = float(speed)
            return 0.5 <= val <= 3.0
        except ValueError:
            return False

    @staticmethod
    def _is_valid_pp_volume(volume: str) -> bool:
        """Check if post-processing volume value is valid (dB number)."""
        try:
            float(volume)
            return True
        except ValueError:
            return False

    @staticmethod
    def _get_pp_speed(settings: Optional['Settings']) -> Optional[str]:
        """Prompt user for post-processing speed (atempo)."""
        pp_config = Config.get_post_processing()
        default = pp_config['default_pp_speed']
        current = settings.pp_speed if settings and settings.pp_speed else default
        console.print('\n[yellow_bold]Post-processing (FFmpeg) — niezależne od modelu TTS:')
        console.print('Przyspieszenie lektora (atempo) od 0.5 do 3.0')
        console.print(f'(obecna: {current}, domyślna: {default}, Enter = bez zmiany)')
        console.print('Wpisz przyspieszenie: ', style='green_bold', end='')
        choice = input().strip()
        if choice and Settings._is_valid_pp_speed(choice):
            return choice
        if not choice:
            return current
        console.print('Niepoprawna wartość. Używam domyślnej wartości.', style='red_bold')
        return default

    @staticmethod
    def _get_pp_volume(settings: Optional['Settings']) -> Optional[str]:
        """Prompt user for post-processing volume (dB)."""
        pp_config = Config.get_post_processing()
        default = pp_config['default_pp_volume']
        current = settings.pp_volume if settings and settings.pp_volume else default
        console.print('\nZmiana głośności lektora w dB (np. 0, 5, -3)')
        console.print(f'(obecna: {current}, domyślna: {default}, Enter = bez zmiany)')
        console.print('Wpisz głośność: ', style='green_bold', end='')
        choice = input().strip()
        if choice and Settings._is_valid_pp_volume(choice):
            return choice
        if not choice:
            return current
        console.print('Niepoprawna wartość. Używam domyślnej wartości.', style='red_bold')
        return default

    @staticmethod
    def _get_output(settings: Optional['Settings']) -> Optional[str]:
        """
            Prompt the user to choose an output option or retrieve it from the user settings.

            Args:
                - settings (Optional['Settings']): The user settings object.

            Returns:
                - Optional[str]: The selected output option or None if not set.
        """

        output = Settings._set_option(
            'Wybierz wyjście: ', Config.get_output())
        if output is None:
            output = settings.output if settings else None
        return output

    @staticmethod
    def get_user_settings(settings_path: str = SETTINGS_PATH) -> Optional['Settings']:
        """
            Get the user settings from a file or prompt the user to enter them.

            Args:
                - settings_path (str): The name of the settings file.

            Returns:
                - Optional['Settings']: The user settings object or None if not found.
        """

        settings = Settings.load_from_file(settings_path)

        translator = Settings._get_translator(settings)
        deepl_api_key = Settings._get_deepl_api_key(settings)
        translated_line_count = Settings._get_translated_line_count(settings)
        tts = Settings._get_tts(settings)
        default_speed, default_volume = Settings._get_default_speed_volume(tts)
        console.print(f'\nWybrałeś: {tts}', style='yellow_bold')
        # Silniki z prędkością/głośnością 'auto' (ElevenBytes itp.) nie mają tych
        # ustawień — nie pytamy o nie, tylko przyjmujemy 'auto'.
        tts_speed = 'auto' if default_speed == 'auto' else Settings._get_tts_speed(tts, default_speed)
        tts_volume = 'auto' if default_volume == 'auto' else Settings._get_tts_volume(tts, default_volume)

        is_elevenbytes = tts in (
            'TTS - ElevenBytes (ElevenLabs v2)',
            'TTS - ElevenBytes (ElevenLabs v3)',
        )
        is_elevenbytes_v3 = tts == 'TTS - ElevenBytes (ElevenLabs v3)'

        elevenbytes_voice = (
            Settings._get_elevenbytes_voice(settings) if is_elevenbytes
            else (settings.elevenbytes_voice if settings else None)
        )
        # voice_settings dotyczą wyłącznie v3 (run7). Dla v2 zachowujemy zapisane wartości.
        elevenbytes_stability: Optional[str]
        elevenbytes_similarity_boost: Optional[str]
        elevenbytes_style: Optional[str]
        elevenbytes_speaker_boost: Optional[str]
        if is_elevenbytes_v3:
            (elevenbytes_stability, elevenbytes_similarity_boost,
             elevenbytes_style, elevenbytes_speaker_boost) = (
                Settings._get_elevenbytes_v3_settings(settings))
        else:
            elevenbytes_stability = settings.elevenbytes_stability if settings else None
            elevenbytes_similarity_boost = settings.elevenbytes_similarity_boost if settings else None
            elevenbytes_style = settings.elevenbytes_style if settings else None
            elevenbytes_speaker_boost = settings.elevenbytes_speaker_boost if settings else None

        pp_speed = Settings._get_pp_speed(settings)
        pp_volume = Settings._get_pp_volume(settings)
        output = Settings._get_output(settings)
        auto_mode = Settings._get_auto_mode(settings)

        return Settings(
            translator=translator,
            deepl_api_key=deepl_api_key,
            translated_line_count=translated_line_count,
            tts=tts,
            tts_speed=tts_speed,
            tts_volume=tts_volume,
            elevenbytes_voice=elevenbytes_voice,
            elevenbytes_stability=elevenbytes_stability,
            elevenbytes_similarity_boost=elevenbytes_similarity_boost,
            elevenbytes_style=elevenbytes_style,
            elevenbytes_speaker_boost=elevenbytes_speaker_boost,
            pp_speed=pp_speed,
            pp_volume=pp_volume,
            output=output,
            auto_mode=auto_mode,
        )

    @staticmethod
    def change_settings_save_to_file(settings_path: str = SETTINGS_PATH) -> None:
        """
            Prompt the user to change the settings and save them to a file.
            If the file does not exist, it will be created.
            If the file exists, it will be overwritten.

            Args:
                - settings_path (str): The name of the settings file.
        """

        settings = Settings.get_user_settings(settings_path)
        assert settings is not None

        with open(settings_path, 'w', encoding='utf-8') as file:
            dump(asdict(settings), file, indent=4)
