import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
from msvcrt import getch
from os import cpu_count, listdir, makedirs, path
from queue import Queue
from shutil import rmtree
from threading import Lock, Thread
from typing import Dict, List, Optional, Set, Tuple

from natsort import natsorted
from rich.console import Console

from constants import (WORKING_SPACE,
                       WORKING_SPACE_OUTPUT,
                       WORKING_SPACE_TEMP,
                       WORKING_SPACE_TEMP_MAIN_SUBS,
                       WORKING_SPACE_TEMP_ALT_SUBS,
                       CONSOLE_THEME,
                       episode_temp_dirs,
                       console)

from data.settings import Settings

from modules.mkvtoolnix import MkvToolNix
from modules.subtitle import SubtitleRefactor
from modules.subtitle_to_speech import SubtitleToSpeech
from modules.translator import SubtitleTranslator
from modules.mkv_processing import MKVProcessing

from utils.cool_animation import CoolAnimation
from utils.execution_timer import execution_timer


# Shared flush lock for standalone per-episode extraction calls.
_EPISODE_PRINT_LOCK: Lock = Lock()


def check_and_create_directories(directories: List[str]):  # ✅
    """
        Checks if the given directories exist, and if not, creates them.

        Args:
            directories (List[str]): A list of directory paths to check and create.
    """
    for directory in directories:
        if not path.exists(directory):
            makedirs(directory)


def display_logo():  # ✅
    """
        Displays the logo of the application using the CoolAnimation class.
    """
    mm_avh_logo: CoolAnimation = CoolAnimation()
    mm_avh_logo.display()
    console.print(
        '╚═══ Multimedia Magic – Audio Visual Heaven ═══╝\n', style='white_bold')


def ask_user(question: str) -> bool:
    """
        Asks the user a yes/no question and returns the response.

        Args:
            question (str): The question to ask the user.

        Returns:
            bool: True if the user answers yes, False otherwise.
    """
    console.print(question, style='bold green', end=' ')
    try:
        return input().lower() in ('t', 'y')
    except (EOFError, KeyboardInterrupt):
        console.print('\n[red_bold]Program przerwany przez użytkownika.')
        sys.exit(0)


def update_settings() -> Settings:  # ✅
    """
        Asks the user if they want to update the settings. If yes, updates the settings and saves them to a file.

        The settings prompt is ALWAYS shown, even when auto_mode is saved — otherwise
        a saved auto_mode=true would trap the user with no way to reach the settings
        menu (auto_mode has no menu entry). Auto only skips the rest of the pipeline
        prompts, never this one.

        Returns:
            Settings: The updated settings.
    """
    if ask_user('💾 Czy chcesz zmienić ustawienia? (T lub Y - tak):'):
        Settings.change_settings_save_to_file()
        console.print('Zapisano ustawienia.\n', style='green_bold')
    else:
        console.print('Pomijam tę opcję.\n', style='red_bold')
    return Settings.load_from_file()


def extract_one_episode(mkv_filename: str, dirs: Optional[Dict[str, str]] = None) -> Tuple[str, bool]:
    """
        Extracts tracks for one MKV into this episode's temp folder.

        Args:
            mkv_filename (str): MKV filename from the shared working_space folder.
            dirs (Optional[Dict[str, str]]): Per-episode temp folders. When None,
                they are derived from the MKV stem.

        Returns:
            Tuple[str, bool]: Episode stem and whether subtitles were already in
                the target language.
    """
    if not mkv_filename.endswith('.mkv'):
        return mkv_filename, False

    stem: str = mkv_filename[:-4]
    if dirs is None:
        dirs = episode_temp_dirs(stem)

    makedirs(dirs['temp'], exist_ok=True)
    makedirs(dirs['main_subs'], exist_ok=True)
    makedirs(dirs['alt_subs'], exist_ok=True)

    buffer: StringIO = StringIO()
    thread_console: Console = Console(
        file=buffer, color_system="truecolor", theme=CONSOLE_THEME,
        force_terminal=True, width=console.size.width)
    mkv: MkvToolNix = MkvToolNix(
        mkv_filename,
        working_space_temp=dirs['temp'],
        console=thread_console)

    try:
        mkv.mkv_extract_track(mkv.get_mkv_info(), auto_mode=True)
    finally:
        # Flush each pre-rendered per-episode log block atomically so parallel
        # auto-mode workers do not interleave their console output.
        with _EPISODE_PRINT_LOCK:
            console.file.write(buffer.getvalue())
            console.file.flush()

    return stem, mkv.subtitle_already_target_lang


def refactor_one_episode(stem: str, dirs: Optional[Dict[str, str]] = None) -> None:
    """
        Refactors one episode's extracted subtitle files inside isolated folders.

        Args:
            stem (str): MKV filename without the .mkv extension.
            dirs (Optional[Dict[str, str]]): Per-episode temp folders.
    """
    if not stem:
        return

    if dirs is None:
        dirs = episode_temp_dirs(stem)

    makedirs(dirs['temp'], exist_ok=True)
    makedirs(dirs['main_subs'], exist_ok=True)
    makedirs(dirs['alt_subs'], exist_ok=True)

    subtitle_extensions: List[str] = [
        '.sup', '.txt', '.ogg',
        '.ssa', '.ass', '.srt',
        '.sub', '.usf', '.vtt',
    ]
    files: List[str] = get_files_with_extensions(dirs['temp'], subtitle_extensions)
    if not files:
        return

    sorted_files: List[str] = natsorted(files)
    for filename in sorted_files:
        subtitle: SubtitleRefactor = SubtitleRefactor(
            filename,
            working_space_temp=dirs['temp'],
            working_space_temp_main_subs=dirs['main_subs'],
            working_space_temp_alt_subs=dirs['alt_subs'])
        if filename.endswith('.ass') or filename.endswith('.ssa'):
            subtitle.split_ass(auto_mode=True)
            subtitle.ass_to_srt()
        if filename.endswith('.srt'):
            subtitle.move_srt()
        if filename.endswith('.txt'):
            subtitle.txt_to_srt(chunk_limit=250,
                                sentence_length=750,
                                split_method='word')


def translate_one_main(stem: str, dirs: Optional[Dict[str, str]], settings: Settings) -> None:
    """
        Translates one episode's main subtitles in its isolated main_subs folder.

        Args:
            stem (str): MKV filename without the .mkv extension.
            dirs (Optional[Dict[str, str]]): Per-episode temp folders.
            settings (Settings): Translation settings.
    """
    if not stem:
        return

    if dirs is None:
        dirs = episode_temp_dirs(stem)

    makedirs(dirs['temp'], exist_ok=True)
    makedirs(dirs['main_subs'], exist_ok=True)
    makedirs(dirs['alt_subs'], exist_ok=True)

    filename: str = stem + '.srt'
    if not path.isfile(path.join(dirs['main_subs'], filename)):
        return

    translator_instance: SubtitleTranslator = SubtitleTranslator()
    translator_instance.translate_srt(filename, dirs['main_subs'], settings)


def translate_one_alt(stem: str, dirs: Optional[Dict[str, str]], settings: Settings) -> None:
    """
        Translates one episode's alternative subtitles when they exist.

        Args:
            stem (str): MKV filename without the .mkv extension.
            dirs (Optional[Dict[str, str]]): Per-episode temp folders.
            settings (Settings): Translation settings.
    """
    if not stem:
        return

    if dirs is None:
        dirs = episode_temp_dirs(stem)

    makedirs(dirs['temp'], exist_ok=True)
    makedirs(dirs['main_subs'], exist_ok=True)
    makedirs(dirs['alt_subs'], exist_ok=True)

    filename: str = stem + '.srt'
    if not path.isfile(path.join(dirs['alt_subs'], filename)):
        return

    translator_instance: SubtitleTranslator = SubtitleTranslator()
    translator_instance.translate_srt(filename, dirs['alt_subs'], settings)


def audio_one_episode(stem: str, dirs: Optional[Dict[str, str]], settings: Settings) -> None:
    """
        Generates and merges TTS audio for one episode in isolated temp folders.

        Args:
            stem (str): MKV filename without the .mkv extension.
            dirs (Optional[Dict[str, str]]): Per-episode temp folders.
            settings (Settings): TTS settings.
    """
    if not stem:
        return

    if dirs is None:
        dirs = episode_temp_dirs(stem)

    makedirs(dirs['temp'], exist_ok=True)
    makedirs(dirs['main_subs'], exist_ok=True)
    makedirs(dirs['alt_subs'], exist_ok=True)
    makedirs(WORKING_SPACE_OUTPUT, exist_ok=True)

    filename: str = stem + '.srt'
    if not path.isfile(path.join(dirs['main_subs'], filename)):
        return

    subtitle_to_speech: SubtitleToSpeech = SubtitleToSpeech(
        filename,
        working_space_temp=dirs['temp'],
        working_space_temp_main_subs=dirs['main_subs'],
        working_space_temp_alt_subs=dirs['alt_subs'])
    subtitle_to_speech.generate_audio(settings)


def output_one_episode(stem: str, settings: Settings) -> None:
    """
        Processes one episode's generated output files into the selected target.

        Args:
            stem (str): MKV filename without the .mkv extension.
            settings (Settings): Output processing settings.
    """
    if not stem:
        return

    dirs: Dict[str, str] = episode_temp_dirs(stem)
    makedirs(dirs['temp'], exist_ok=True)
    makedirs(dirs['main_subs'], exist_ok=True)
    makedirs(dirs['alt_subs'], exist_ok=True)
    makedirs(WORKING_SPACE_OUTPUT, exist_ok=True)

    filename: str = stem + '.srt'
    if path.isfile(path.join(dirs['alt_subs'], filename)):
        subtitle: SubtitleRefactor = SubtitleRefactor(
            filename,
            working_space_temp=dirs['temp'],
            working_space_temp_main_subs=dirs['main_subs'],
            working_space_temp_alt_subs=dirs['alt_subs'])
        subtitle.srt_to_ass()

    files: List[str] = listdir(WORKING_SPACE_OUTPUT)
    episode_files: List[str] = [
        file for file in files
        if path.splitext(file)[0] == stem and not file.endswith(('.mkv', '.mp4'))
    ]
    if not episode_files:
        return

    subtitle_processor: MKVProcessing = MKVProcessing(filename=stem,
                                                      crf_value='18',
                                                      preset_value='medium')
    subtitle_processor.process_mkv(settings)


# Sentinel put on a pipeline queue to signal "no more items" to its consumer.
_PIPELINE_DONE: object = object()


def _log_episode(stem: str, message: str, style: str = 'blue_bold') -> None:
    """Print a pipeline message tagged with the episode, atomically.

    Parallel pipeline stages share one console; the lock keeps a tagged line
    from landing in the middle of another stage's output.

    Args:
        stem: Episode identifier shown as a prefix.
        message: Text to print.
        style: Rich style name.
    """
    with _EPISODE_PRINT_LOCK:
        console.print(f'[{stem}] {message}', style=style)


def run_auto_pipeline(settings: Settings) -> None:
    """Process every episode as a 3-stage pipeline so stages overlap in time.

    Stages run concurrently as separate threads connected by queues, so while
    episode N is being voiced, episode N+1 is already being translated (they use
    different APIs, so they do not fight over the same rate limit):

        PREP thread  : extract -> refactor -> translate main -> (queue AUDIO)
                       -> translate alt      (per episode, sequential)
        AUDIO thread : take stem -> generate+merge audio -> (queue OUTPUT)
        OUTPUT thread: take stem -> build final mkv/mp4

    Each episode lives in its own temp/<stem>/ folder (see episode_temp_dirs), so
    concurrent stages never touch another episode's files — this is what makes
    the overlap safe (no cross-episode file races). A failure in one episode is
    isolated: it is logged and the episode is dropped, the pipeline keeps running.

    At most 3 episodes are in flight (one per stage), which keeps the audio API
    load bounded (audio itself already fans out ~85 requests per episode).

    Args:
        settings: Pipeline settings (translator, tts, output target).
    """
    mkv_files: List[str] = natsorted(get_mkv_files(WORKING_SPACE))
    if not mkv_files:
        console.print('Brak plików MKV do przetworzenia.', style='red_bold')
        return

    audio_queue: "Queue[object]" = Queue()
    output_queue: "Queue[object]" = Queue()

    def _prep_stage() -> None:
        """Extract, refactor and translate each episode; feed the audio queue."""
        try:
            for mkv_filename in mkv_files:
                stem: str = mkv_filename[:-4] if mkv_filename.endswith('.mkv') else mkv_filename
                dirs: Dict[str, str] = episode_temp_dirs(stem)
                try:
                    _log_episode(stem, 'Wypakowywanie...', style='yellow_bold')
                    resolved_stem, already_polish = extract_one_episode(mkv_filename, dirs)
                    refactor_one_episode(resolved_stem, dirs)
                    if not already_polish:
                        _log_episode(resolved_stem, 'Tłumaczenie...', style='yellow_bold')
                        translate_one_main(resolved_stem, dirs, settings)
                    # Main is ready -> audio can start now, in parallel with the
                    # next episode's translation.
                    audio_queue.put(resolved_stem)
                    # Alt subtitles come after main and do not block audio.
                    if not already_polish:
                        translate_one_alt(resolved_stem, dirs, settings)
                except Exception as exc:
                    _log_episode(stem, f'Błąd (prep): {exc}', style='red_bold')
        finally:
            audio_queue.put(_PIPELINE_DONE)

    def _audio_stage() -> None:
        """Consume ready episodes, voice them, feed the output queue."""
        try:
            while True:
                item: object = audio_queue.get()
                if item is _PIPELINE_DONE:
                    break
                stem = str(item)
                dirs = episode_temp_dirs(stem)
                try:
                    _log_episode(stem, 'Generowanie audio...', style='yellow_bold')
                    audio_one_episode(stem, dirs, settings)
                    output_queue.put(stem)
                except Exception as exc:
                    _log_episode(stem, f'Błąd (audio): {exc}', style='red_bold')
        finally:
            output_queue.put(_PIPELINE_DONE)

    def _output_stage() -> None:
        """Consume voiced episodes and build the final output file."""
        while True:
            item = output_queue.get()
            if item is _PIPELINE_DONE:
                break
            stem = str(item)
            try:
                _log_episode(stem, 'Przetwarzanie wyjścia...', style='yellow_bold')
                output_one_episode(stem, settings)
                _log_episode(stem, 'Gotowe.', style='green_bold')
            except Exception as exc:
                _log_episode(stem, f'Błąd (wyjście): {exc}', style='red_bold')

    prep: Thread = Thread(target=_prep_stage, name='prep')
    audio: Thread = Thread(target=_audio_stage, name='audio')
    output: Thread = Thread(target=_output_stage, name='output')
    for thread in (prep, audio, output):
        thread.start()
    for thread in (prep, audio, output):
        thread.join()


def extract_tracks_from_mkv(auto: bool = False) -> Set[str]:  # ✅
    """
        Extracts tracks from MKV files.

        In manual mode the user is asked whether to extract; in auto mode the
        audio and subtitle tracks are picked automatically for every MKV file
        without any prompt.

        Args:
            auto (bool): When True, skip the prompt and auto-select tracks.

        Returns:
            Set[str]: Base file names whose subtitles are already Polish (skip
                translation in auto mode).
    """
    already_polish: Set[str] = set()
    if not (auto or ask_user('🧲 Czy chcesz wyciągnąć ścieżki z plików mkv? (T lub Y - tak):')):
        console.print('Pomijam tę opcję.\n', style='red_bold')
        return already_polish

    files: List[str] = get_mkv_files(WORKING_SPACE)
    sorted_files: List[str] = natsorted(files)
    if not sorted_files:
        return already_polish

    # Extraction is I/O-bound (mkvextract subprocess + disk), so threads scale it
    # well on an SSD. A per-file failure must not abort the rest of the batch.
    polish_lock: Lock = Lock()
    # Guards atomic flushing of each thread's buffered output (auto mode only)
    # so per-file blocks are never interleaved in the shared console.
    print_lock: Lock = Lock()

    def _extract_one(filename: str) -> None:
        # In manual mode _prompt_tracks_to_extract() calls input(), so output
        # must go straight to the real console — buffering would hide the
        # prompt from the user and desync it from their answer. Only auto mode
        # (no prompts) can safely buffer per-thread and flush as one block.
        if auto:
            buffer: StringIO = StringIO()
            thread_console: Console = Console(
                file=buffer, color_system="truecolor", theme=CONSOLE_THEME,
                force_terminal=True, width=console.size.width)
            mkv: MkvToolNix = MkvToolNix(filename, console=thread_console)
        else:
            mkv = MkvToolNix(filename)

        try:
            mkv.mkv_extract_track(mkv.get_mkv_info(), auto_mode=auto)
        finally:
            if auto:
                # Write the pre-rendered ANSI text straight to the console's
                # underlying stream. console.print() must NOT be used here: it
                # would re-parse the already-rendered escape codes as plain
                # text (highlighting the "[" / "]" bytes) and corrupt them.
                with print_lock:
                    console.file.write(buffer.getvalue())
                    console.file.flush()

        if mkv.subtitle_already_target_lang:
            with polish_lock:
                already_polish.add(filename[:-4])

    workers: int = _parallelism(len(sorted_files), cap=6)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(_extract_one, name): name for name in sorted_files}
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                future.result()
            except Exception as exc:
                # Same lock as the per-file flush: keeps this line from landing
                # in the middle of another thread's buffered block.
                with print_lock:
                    console.print(
                        f'Błąd wypakowywania {name}: {exc}', style='red_bold')

    return already_polish


def get_mkv_files(directory: str) -> List[str]:
    """
        Gets all MKV files in a directory.

        Args:
            directory (str): The directory to search for MKV files.

        Returns:
            List[str]: A list of MKV files in the directory.
    """
    return [file for file in listdir(directory)
            if path.isfile(path.join(directory, file)) and file.endswith('.mkv')]


def refactor_subtitles(auto: bool = False):  # ✅
    """
        Refactors subtitles in various formats to a standard format.

        Args:
            auto (bool): When True, ASS/SSA styles are split automatically by the
                classifier instead of asking the user.
    """
    subtitle_extensions: List[str] = [
        '.sup', '.txt', '.ogg',
        '.ssa', '.ass', '.srt',
        '.sub', '.usf', '.vtt',
    ]

    files: List[str] = get_files_with_extensions(
        WORKING_SPACE_TEMP, subtitle_extensions)
    sorted_files: List[str] = natsorted(files)
    for filename in sorted_files:
        refactor_subtitle_file(filename, auto=auto)


def get_files_with_extensions(directory: str, extensions: List[str]) -> List[str]:
    """
        Gets all files in a directory with certain extensions.

        Args:
            directory (str): The directory to search for files.
            extensions (List[str]): The extensions to look for.

        Returns:
            List[str]: A list of files in the directory with the specified extensions.
    """
    return [
        file for file in listdir(directory)
        if (
            path.isfile(path.join(directory, file)) and
            any(file.endswith(ext) for ext in extensions)
        )
    ]


def refactor_subtitle_file(filename: str, auto: bool = False):
    """
        Refactors a subtitle file to a standard format.

        Args:
            filename (str): The name of the subtitle file to refactor.
            auto (bool): When True, ASS/SSA styles are split automatically by the
                classifier instead of asking the user.
    """
    subtitle: SubtitleRefactor = SubtitleRefactor(filename)
    if filename.endswith('.ass') or filename.endswith('.ssa'):
        subtitle.split_ass(auto_mode=auto)
        subtitle.ass_to_srt()
    if filename.endswith('.srt'):
        subtitle.move_srt()
    if filename.endswith('.txt'):
        subtitle.txt_to_srt(chunk_limit=250,
                            sentence_length=750,
                            split_method='word')


def translate_subtitles(settings: Settings, auto: bool = False,
                        already_polish: Set[str] | None = None):  # ✅
    """
        Translates subtitle files.

        In manual mode the user is asked whether to translate and which files; in
        auto mode every file is translated without any prompt, except files whose
        subtitles are already Polish.

        Args:
            settings (Settings): The settings to use for translation.
            auto (bool): When True, skip the prompts and translate all files.
            already_polish (Set[str] | None): Base names of files whose subtitles
                are already Polish; skipped in auto mode.
    """
    if not auto and not ask_user('💭 Czy chcesz tłumaczyć pliki napisów? (T lub Y - tak):'):
        console.print('Pomijam tę opcję.\n', style='red_bold')
        return

    already_polish = already_polish or set()
    main_subs_files = get_srt_files(WORKING_SPACE_TEMP_MAIN_SUBS)
    if auto:
        files_to_translate: Dict[str, bool] = {}
        for filename in main_subs_files:
            if filename[:-4] in already_polish:
                console.print(
                    f'AUTO: pomijam tłumaczenie (napisy już PL): {filename}',
                    style='green_bold')
                files_to_translate[filename] = False
            else:
                files_to_translate[filename] = True
    else:
        files_to_translate = ask_to_translate_files(main_subs_files)
    translate_files(files_to_translate, settings)


def get_srt_files(directory: str) -> List[str]:
    """
        Gets all SRT files in a directory.

        Args:
            directory (str): The directory to search for SRT files.

        Returns:
            List[str]: A list of SRT files in the directory.
    """
    return natsorted([
        filename for filename in listdir(directory)
        if path.isfile(path.join(directory, filename)) and filename.endswith('.srt')
    ])


def ask_to_translate_files(files: List[str]) -> dict:
    """
        Asks the user which files they want to translate.

        Args:
            files (List[str]): A list of files to ask about.

        Returns:
            dict: A dictionary mapping file names to a boolean indicating whether the user wants to translate them.
    """
    files_to_translate: dict = {}
    for filename in files:
        console.print("\nTŁUMACZENIE PLIKU:", style='yellow_bold')
        console.print(filename, style='white_bold')
        if ask_user("Czy chcesz przetłumaczyć (T lub Y - tak):"):
            files_to_translate[filename] = True
        else:
            console.print('Pomijam tę opcję.\n', style='red_bold')
            files_to_translate[filename] = False

    return files_to_translate


def translate_files(files_to_translate: dict, settings: Settings):
    """
        Translates the specified files.

        Args:
            files_to_translate (dict): A dictionary mapping file names to a boolean indicating whether to translate them.
            settings (Settings): The settings to use for translation.
    """
    translator_instance: SubtitleTranslator = SubtitleTranslator()

    for filename, should_translate in files_to_translate.items():
        if should_translate:
            translator_instance.translate_srt(filename,
                                              WORKING_SPACE_TEMP_MAIN_SUBS,
                                              settings)
            if path.exists(path.join(WORKING_SPACE_TEMP_ALT_SUBS, filename)):
                translator_instance.translate_srt(filename,
                                                  WORKING_SPACE_TEMP_ALT_SUBS,
                                                  settings)


def convert_numbers_to_words():  # ✅
    """
        Asks the user if they want to convert numbers to words in the text. If yes, performs the conversion.
    """
    if not ask_user('🔢 Czy chcesz przekonwertować liczby na słowa w tekście? (T lub Y - tak):'):
        console.print('Pomijam tę opcję.\n', style='red_bold')
        return

    srt_files = get_srt_files(WORKING_SPACE_TEMP_MAIN_SUBS)
    convert_numbers_in_files(srt_files)


def convert_numbers_in_files(files: List[str]):
    """
        Converts numbers to words in the specified files.

        Args:
            files (List[str]): A list of files to convert numbers in.
    """
    for filename in files:
        console.print(
            "\nKONWERSJA LICZB (BEZ POPRAWNOŚCI GRAMATYCZNEJ) W PLIKU:", style='yellow_bold')
        console.print(filename, style='white_bold')
        if ask_user("Czy chcesz przekonwertować liczby na słowa w tym pliku? (T lub Y - tak):"):
            subtitle: SubtitleRefactor = SubtitleRefactor(filename)
            subtitle.convert_numbers_in_srt()
        else:
            console.print(f'Pomijam plik {filename}.\n', style='red_bold')


def generate_audio_for_subtitles(settings: Settings, auto: bool = False) -> None:  # ✅
    """
        Generates audio for subtitles.

        In manual mode the user is asked whether to generate audio and for which
        files; in auto mode audio is generated for every file without any prompt.

        Args:
            settings (Settings): The settings to use for audio generation.
            auto (bool): When True, skip the prompts and generate audio for all files.
    """
    if not auto and not ask_user('🎤 Czy chcesz generować audio dla napisów? (T lub Y - tak):'):
        console.print('Pomijam tę opcję.\n', style='red_bold')
        return

    main_subs_files: List[str] = get_srt_files(WORKING_SPACE_TEMP_MAIN_SUBS)
    if auto:
        files_to_generate_audio: Dict[str, bool] = {
            filename: True for filename in main_subs_files}
    else:
        files_to_generate_audio = ask_to_generate_audio_files(main_subs_files)
    generate_audio_files(files_to_generate_audio, settings, auto=auto)


def ask_to_generate_audio_files(files: List[str]) -> Dict[str, bool]:
    """
        Asks the user which files they want to generate audio for.

        Args:
            files (List[str]): A list of files to ask about.

        Returns:
            dict: A dictionary mapping file names to a boolean indicating whether the user wants to generate audio for them.
    """
    files_to_generate_audio: Dict[str, bool] = {}
    for filename in files:
        console.print("\nGENEROWANIE AUDIO DLA PLIKU:", style='yellow_bold')
        console.print(filename, style='white_bold')
        if ask_user("Czy chcesz wygenerować audio dla tego pliku? (T lub Y - tak):"):
            files_to_generate_audio[filename] = True
        else:
            console.print('Pomijam tę opcję.', style='red_bold')
            files_to_generate_audio[filename] = False
    return files_to_generate_audio


def generate_audio_files(files_to_generate_audio: Dict[str, bool], settings: Settings,
                         auto: bool = False) -> None:
    """
        Generates audio for the specified files.

        Audio is generated one file at a time and merged inline. Background merge
        was tried but is unsafe here: merge_tts_audio() scans the SHARED main_subs/
        temp dirs and removes files by name, so a merge running in the background
        would race the next file's audio generation and could delete/merge the
        wrong episode's files — a silent audio-loss regression. Real overlap would
        require per-episode temp folders (a larger change); until then, correctness
        beats speed and merge stays inline in both modes.

        Args:
            files_to_generate_audio (Dict[str, bool]): A dictionary mapping file names to a boolean indicating whether the user wants to generate audio for them.
            settings (Settings): The settings to use for audio generation.
            auto (bool): Kept for signature compatibility; merge stays inline in
                both modes for correctness.
    """
    for filename, should_generate_audio in files_to_generate_audio.items():
        if should_generate_audio:
            SubtitleToSpeech(filename).generate_audio(settings)


def refactor_alt_subtitles():  # ✅
    """
        Refactors alternative subtitles to a standard format.
    """
    files: List[str] = get_srt_files(WORKING_SPACE_TEMP_ALT_SUBS)
    sorted_files: List[str] = natsorted(files)
    for filename in sorted_files:
        subtitle: SubtitleRefactor = SubtitleRefactor(filename)
        subtitle.srt_to_ass()


def process_output_files(settings: Settings):
    """
        Processes output files based on user settings.

        Args:
            settings (Settings): The settings to use for processing.
    """
    files = listdir(WORKING_SPACE_OUTPUT)
    files_dict: Dict[str, List[str]] = {path.splitext(file)[0]: [] for file in files}
    for file in files:
        if not file.endswith(('.mkv', '.mp4')):
            files_dict[path.splitext(file)[0]].append(file)

    for base_name, files in files_dict.items():
        if len(files) > 0:
            # https://trac.ffmpeg.org/wiki/Encode/H.264
            # crf_value => 0 ... 18 ... 23 ... 51 ... :(
            # preset_value => 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow', 'placebo'
            subtitle_processor = MKVProcessing(filename=base_name,
                                               crf_value='18',
                                               preset_value='medium')
            subtitle_processor.process_mkv(settings)


def clear_temp_folders():
    """
        Clears temporary folders used during processing.
    """
    folders = [WORKING_SPACE_TEMP, WORKING_SPACE_TEMP_MAIN_SUBS,
               WORKING_SPACE_TEMP_ALT_SUBS]
    for folder in folders:
        rmtree(folder, ignore_errors=True)
        makedirs(folder, exist_ok=True)


def _parallelism(item_count: int, cap: int) -> int:
    """Pick a worker count that scales with the machine but never overshoots.

    Never spawns more workers than there are items or CPU cores, and clamps to a
    per-stage cap (I/O stages want a lower cap than the core count). Always ≥1.

    Args:
        item_count: How many items the stage will process.
        cap: Upper bound appropriate for this stage's workload (I/O vs CPU).

    Returns:
        Worker count in the range [1, min(item_count, cpu_count, cap)].
    """
    cores: int = cpu_count() or 1
    return max(1, min(item_count, cores, cap))


@execution_timer  # ✅
def main():
    """
        Main function that runs the entire process.

        When settings.auto_mode is True the pipeline runs unattended: every step
        executes automatically (tracks, styles, translation and audio), decisions
        are logged instead of prompted, and number-to-words conversion is skipped
        (the user's preference). Otherwise the interactive flow is unchanged.
    """
    display_logo()
    # Settings prompt is always shown first (even in auto mode), so the user can
    # always reach the menu. auto_mode is read AFTER, from the possibly-updated
    # settings, and governs only the rest of the pipeline.
    settings: Settings = update_settings()
    auto: bool = settings.auto_mode
    if auto:
        # Auto mode runs the overlapping per-episode pipeline (extract -> refactor
        # -> translate -> audio -> output) instead of the sequential batch stages,
        # so episodes' stages overlap in time. Each episode is isolated in its own
        # temp/<stem>/ folder, so nothing races on shared files.
        console.print(
            'TRYB AUTOMATYCZNY — potok równoległy (odcinki nakładane).\n',
            style='green_bold')
        run_auto_pipeline(settings)
        clear_temp_folders()
        return

    already_polish: Set[str] = extract_tracks_from_mkv(auto=auto)
    refactor_subtitles(auto=auto)
    translate_subtitles(settings, auto=auto, already_polish=already_polish)
    convert_numbers_to_words()
    generate_audio_for_subtitles(settings, auto=auto)
    refactor_alt_subtitles()
    process_output_files(settings)
    clear_temp_folders()


if __name__ == '__main__':
    """
        Ensures the main function is only run if the script is executed directly (not imported as a module).
    """
    directories: List[str] = [WORKING_SPACE, WORKING_SPACE_OUTPUT,
                              WORKING_SPACE_TEMP, WORKING_SPACE_TEMP_MAIN_SUBS, WORKING_SPACE_TEMP_ALT_SUBS]
    check_and_create_directories(directories)
    try:
        main()

        console.print(
            '\n[green_italic]Naciśnij dowolny klawisz, aby zakończyć działanie programu...', end='')
        getch()
    except (KeyboardInterrupt, EOFError):
        console.print('\n[yellow_bold]Program zakończony.')
        sys.exit(0)

