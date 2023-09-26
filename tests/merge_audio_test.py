# pip inatall termcolor
import subprocess
import os
from termcolor import cprint


def cmd(command):
    subprocess.call(command, shell=True)


def merge_audio():
    cprint("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝",
           'white', attrs=['bold'])
    print("")
    file_extension_1 = input(
        "Podaj rozszerzenie pliku z dźwiękiem np.: eac3, aac: ")
    filr_extension_2 = input(
        "Podaj rozszerzenie pliku z dźwiękiem lektora (+7db) np.: wav: ")
    for file in os.listdir('./'):
        if file.endswith(file_extension_1) and file[:-len(file_extension_1)] + filr_extension_2 in os.listdir('./'):
            cmd('ffmpeg -i ./' + file + ' -i ./' + file[:-len(file_extension_1)] + filr_extension_2 +
                ' -filter_complex "[1:a]volume=7dB[a1];[0:a][a1]amix=inputs=2:duration=first" ./' + file + '_' + file[:-len(file_extension_1)] + filr_extension_2 + '+7db.eac3')


merge_audio()
