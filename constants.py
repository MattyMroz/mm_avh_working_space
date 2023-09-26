"""
    This script defines various paths to files and folders that are used in the project.
    It also includes definitions of styles for the rich library, which is used for printing colored text in the console.

    * Example usage:
        from constants import SETTINGS_PATH, WORKING_SPACE, console

    Variables:
        - SETTINGS_PATH: Path to the settings file.
        - WORKING_SPACE: Main working path.
        - WORKING_SPACE_OUTPUT: Path to the output folder.
        - WORKING_SPACE_TEMP: Path to the temporary folder.
        - WORKING_SPACE_TEMP_MAIN_SUBS: Path to the folder with main subtitles.
        - WORKING_SPACE_TEMP_ALT_SUBS: Path to the folder with alternative subtitles.
        - MKVTOOLNIX_FOLDER: Path to the mkvtoolnix folder.
        - MKV_EXTRACT_PATH: Path to the mkvextract.exe file.
        - MKV_MERGE_PATH: Path to the mkvmerge.exe file.
        - MKV_INFO_PATH: Path to the mkvinfo.exe file.
        - MKV_PROPEDIT_PATH: Path to the mkvpropedit.exe file.
        - BALABOLKA_FOLDER: Path to the balabolka folder.
        - FFMPEG_FOLDER: Path to the ffmpeg folder.
        - BALABOLKA_PATH: Path to the balcon.exe file.
        - FFMPEG_PATH: Path to the ffmpeg.exe file.
        - console: Instance of the Console class from the rich library, defined with various styles.
"""

from os import getcwd, pardir, path
from rich.console import Console
from rich.theme import Theme

# Path for settings
SETTINGS_PATH: str = path.join(getcwd(), 'data', 'settings.json')

# Main paths
WORKING_SPACE: str = path.join(getcwd(), 'working_space')
WORKING_SPACE_OUTPUT: str = path.join(WORKING_SPACE, 'output')
WORKING_SPACE_TEMP: str = path.join(WORKING_SPACE, 'temp')
WORKING_SPACE_TEMP_MAIN_SUBS: str = path.join(WORKING_SPACE_TEMP, 'main_subs')
WORKING_SPACE_TEMP_ALT_SUBS: str = path.join(WORKING_SPACE_TEMP, 'alt_subs')

# Paths for mkvtoolnix
MKVTOOLNIX_FOLDER: str = path.join(
    path.abspath(path.join(getcwd(), pardir)),
    'mm_avh_working_space', 'bin', 'mkvtoolnix'
)
MKV_EXTRACT_PATH: str = path.join(MKVTOOLNIX_FOLDER, 'mkvextract.exe')
MKV_MERGE_PATH: str = path.join(MKVTOOLNIX_FOLDER, 'mkvmerge.exe')
MKV_INFO_PATH: str = path.join(MKVTOOLNIX_FOLDER, 'mkvinfo.exe')
MKV_PROPEDIT_PATH = path.join(MKVTOOLNIX_FOLDER, 'mkvpropedit.exe')

# Paths for balabolka and ffmpeg
BALABOLKA_FOLDER: str = path.join(
    path.abspath(path.join(getcwd(), pardir)),
    'mm_avh_working_space', 'bin', 'balabolka'
)
FFMPEG_FOLDER: str = path.join(
    path.abspath(path.join(getcwd(), pardir)),
    'mm_avh_working_space', 'bin', 'ffmpeg', 'bin'
)
BALABOLKA_PATH: str = path.join(BALABOLKA_FOLDER, 'balcon.exe')
FFMPEG_PATH: str = path.join(FFMPEG_FOLDER, 'ffmpeg.exe')


# Rich print styles
console: Console = Console(theme=Theme({
    "purple_bold": "purple bold",
    "purple_italic": "purple italic",
    "pink_bold": "pale_violet_red1 bold",
    "pink_italic": "pale_violet_red1 italic",
    "red_bold": "bright_red bold",
    "red_italic": "bright_red italic",
    "brown_bold": "rgb(180,82,45) bold",
    "brown_italic": "rgb(180,82,45) italic",
    "orange_bold": "rgb(255,135,70) bold",
    "orange_italic": "rgb(255,135,70) italic",
    "yellow_bold": "bright_yellow bold",
    "yellow_italic": "bright_yellow italic",
    "green_bold": "green bold",
    "green_italic": "green italic",
    "blue_bold": "dodger_blue2 bold",
    "blue_italic": "dodger_blue2 italic",
    "white_bold": "white bold",
    "white_italic": "white italic",
    "normal_bold": "bold",
    "normal_italic": "italic",
    "black_bold": "rgb(0,0,0) on white bold",
    "black_italic": "rgb(0,0,0) on white italic",
    "repr.number": "bright_red bold",
}))

# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="purple_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="purple_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="pink_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="pink_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="red_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="red_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="brown_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="brown_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="orange_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="orange_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="yellow_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="yellow_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="green_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="green_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="blue_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="blue_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="white_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="white_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="normal_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="normal_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="black_bold")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="black_italic")
# console.print("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝", style="repr.number")
# input()
