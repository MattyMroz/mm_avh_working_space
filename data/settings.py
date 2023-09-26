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
        "chat_gpt_access_token": null,
        "translated_line_count": "50",
        "tts": "TTS - Agnieszka - Ivona",
        "tts_speed": "5",
        "tts_volume": "65",
        "output": "Ogl\u0105dam w MM_AVH_Players (wynik: napisy i audio)"
        }
"""

from dataclasses import asdict, dataclass
from json import decoder, dump, load
from typing import Dict, List, Optional, Tuple
import webbrowser

from constants import SETTINGS_PATH, console
from data.config import Config


@dataclass(slots=True)
class Settings:
    """
        A class representing application settings.

        Attributes:
            - translator (Optional[str]): The selected translator.
            - deepl_api_key (Optional[str]): The API key for DeepL translation service.
            - chat_gpt_access_token (Optional[str]): The access token for ChatGPT API.
            - translated_line_count (Optional[str]): The number of translated lines.
            - tts (Optional[str]): The selected TTS engine.
            - tts_speed (Optional[str]): The speed of the TTS voice.
            - tts_volume (Optional[str]): The volume of the TTS voice.
            - output (Optional[str]): The selected output option.

        Methods:
            - load_from_file(cls, settings_path: str) -> 'Settings': Load settings from a file.
            - _set_option(prompt: str, options: List[Dict[str, str]]) -> str | None: Set an option from a list of options.
            - _is_valid_speed(speed: str, tts: str) -> bool: Check if a given speed value is valid for the selected TTS engine.
            - _is_valid_volume(volume: str, tts: str) -> bool: Check if a given volume value is valid for the selected TTS engine.
            - _get_translator(settings: Optional['Settings']) -> Optional[str]: Get the selected translator.
            - _get_deepl_api_key(settings: Optional['Settings']) -> Optional[str]: Get the DeepL API key.
            - _get_chat_gpt_access_token(settings: Optional['Settings']) -> Optional[str]: Get the ChatGPT access token.
            - _get_translated_line_count(settings: Optional['Settings']) -> Optional[str]: Get the number of translated lines.
            - _get_tts(settings: Optional['Settings']) -> Optional[str]: Get the selected TTS engine.
            - _get_default_speed_volume(tts: str) -> Tuple[Optional[str], Optional[str]]: Get the default speed and volume for a TTS engine.
            - _get_tts_speed(tts: str, default_speed: Optional[str]) -> Optional[str]: Get the TTS speed.
            - _get_tts_volume(tts: str, default_volume: Optional[str]) -> Optional[str]: Get the TTS volume.
            - _get_output(settings: Optional['Settings']) -> Optional[str]: Get the selected output option.
            - get_user_settings(settings_path: str) -> Optional['Settings']: Get user settings from a file.
            - change_settings_save_to_file(settings_path: str) -> None: Change and save settings to a file.
    """
    translator: Optional[str] = None
    deepl_api_key: Optional[str] = None
    chat_gpt_access_token: Optional[str] = None
    translated_line_count: Optional[str] = None
    tts: Optional[str] = None
    tts_speed: Optional[str] = None
    tts_volume: Optional[str] = None
    output: Optional[str] = None

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
                chat_gpt_access_token=None,
                translated_line_count='50',
                tts='TTS - Agnieszka - Ivona',
                tts_speed='5',
                tts_volume='65',
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

        return Settings(
            translator=data.get('translator'),
            deepl_api_key=data.get('deepl_api_key'),
            chat_gpt_access_token=data.get('chat_gpt_access_token'),
            translated_line_count=data.get('translated_line_count'),
            tts=data.get('tts'),
            tts_speed=data.get('tts_speed'),
            tts_volume=data.get('tts_volume'),
            output=data.get('output')
        )

    @staticmethod
    def _set_option(prompt: str, options: List[Dict[str, str]]) -> str | None:
        """
            Set an option from a list of options.

            Args:
                - prompt (str): The prompt to display to the user.
                - options (List[Dict[str, str]]): The list of options to choose from.

            Returns:
                - str | None: The selected option, or None if the selection is invalid.
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
    def _is_valid_speed(speed: str, tts: str) -> bool:
        """
            Check if a given speed value is valid for the selected TTS engine.

            Args:
                - speed (str): The speed value to check.
                - tts (str): The selected TTS engine.

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
    def _is_valid_volume(volume: str, tts: str) -> bool:
        """
            Check if a given volume value is valid for the selected TTS engine.

            Args:
                - volume (str): The volume value to check.
                - tts (str): The selected TTS engine.

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
            deepl_api_key = input('')
            if deepl_api_key == '':
                deepl_api_key = settings.deepl_api_key if settings else None
                console.print(
                    'Niepoprawna wartość. Nie zmieniono wartości!', style='red_bold')
        else:
            deepl_api_key = settings.deepl_api_key if settings else None
        return deepl_api_key

    @staticmethod
    def _get_chat_gpt_access_token(settings: Optional['Settings']) -> Optional[str]:
        """
            Prompt the user to set the Chat GPT access token or retrieve it from the user settings.

            Args:
                - settings (Optional['Settings']): The user settings object.

            Returns:
                - Optional[str]: The Chat GPT access token or None if not set.
        """

        console.print(
            '\nCzy chcesz ustawić token dostępu do chat GPT?', style='yellow_bold')
        console.print('(T lub Y - tak): ', style='green_bold',
                      end='')
        if input().lower() in ('t', 'y'):
            console.print(
                'Token dostępu (accessToken): https://chat.openai.com/api/auth/session', style='yellow_bold')
            webbrowser.open('https://chat.openai.com/api/auth/session')
            console.print(
                'Podaj token dostępu do chat GPT: ', style='green_bold', end='')
            chat_gpt_access_token = input()
            if chat_gpt_access_token == '':
                chat_gpt_access_token = settings.chat_gpt_access_token if settings else None
                console.print(
                    'Niepoprawna wartość. Nie zmieniono wartości!', style='red_bold')
        else:
            chat_gpt_access_token = settings.chat_gpt_access_token if settings else None
        return chat_gpt_access_token

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
    def _get_default_speed_volume(tts: str) -> Tuple[Optional[str], Optional[str]]:
        """
            Retrieve the default voice speed and volume for the specified TTS engine.

            Args:
                - tts (str): The selected TTS engine.

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
    def _get_tts_speed(tts: str, default_speed: Optional[str]) -> Optional[str]:
        """
            Prompt the user to enter the voice speed for the selected TTS engine, or use the default speed.

            Args:
                - tts (str): The selected TTS engine.
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
    def _get_tts_volume(tts: str, default_volume: Optional[str]) -> Optional[str]:
        """
            Prompt the user to enter the voice volume for the selected TTS engine, or use the default volume.

            Args:
                - tts (str): The selected TTS engine.
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
        chat_gpt_access_token = Settings._get_chat_gpt_access_token(settings)
        translated_line_count = Settings._get_translated_line_count(settings)
        tts = Settings._get_tts(settings)
        default_speed, default_volume = Settings._get_default_speed_volume(tts)
        console.print(f'\nWybrałeś: {tts}', style='yellow_bold')
        tts_speed = Settings._get_tts_speed(tts, default_speed)
        tts_volume = Settings._get_tts_volume(tts, default_volume)
        output = Settings._get_output(settings)

        return Settings(
            translator=translator,
            deepl_api_key=deepl_api_key,
            chat_gpt_access_token=chat_gpt_access_token,
            translated_line_count=translated_line_count,
            tts=tts,
            tts_speed=tts_speed,
            tts_volume=tts_volume,
            output=output
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

        with open(settings_path, 'w', encoding='utf-8') as file:
            dump(asdict(settings), file, indent=4)
