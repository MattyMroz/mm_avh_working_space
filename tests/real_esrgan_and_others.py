# Jak pobrać FFmpeg w Windows
# https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z -- auto pobieranie
# Zmienne środowiskowe użytkownika -> w PATH dodaj ścieżkę do folderu: C:\FFmpeg\bin
# cmd ffmpeg -version - czy działa
# pip install opencv-python
# pip install pillow
# pip install termcolor
import subprocess
import time
from PIL import Image
import cv2
import os
from termcolor import cprint


def cmd(command):
    subprocess.call(command, shell=True)


def hight_quality_image_real_esrgan_x4_plus_anime():
    cmd('realesrgan-ncnn-vulkan.exe -i ./input -o ./output -n realesrgan-x4plus-anime')


def fast_image_real_esrgan_animevideov3_x4():
    cmd('realesrgan-ncnn-vulkan.exe -i ./input -o ./output -n realesr-animevideov3-x4')


def fast_image_real_esrgan_animevideov3_x4_jpg():
    cmd('realesrgan-ncnn-vulkan.exe -i ./input -o ./output -n realesr-animevideov3-x4 -f jpg')


def slow_image_real_esrgan_x4_plus():
    cmd('realesrgan-ncnn-vulkan.exe -i ./input -o ./output -n realesrgan-x4plus')


def clean():
    # Usuń folder tmp_frames i out_frames
    cmd('rmdir /s /q tmp_frames')
    cmd('rmdir /s /q out_frames')

    # Przywróć folder tmp_frames i out_frames
    cmd('mkdir tmp_frames')
    cmd('mkdir out_frames')


def add_info():
    # Dodaj info o plkiu wideo
    filename = input("Podaj nazwę pliku np.: 1.mp4: ")

    print("FPS: ")
    cmd('ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 ./input/' + filename)

    print("Wpisz powyższą ilość FPS np.: 500: ")
    fps = input("Podaj ilość FPS: ")

    return filename, fps


def video_to_frames(filename):
    # FFmpeg pobierze klatki z wideo i zapisze je w folderze tmp_frames
    cmd('ffmpeg -i ./input/' + filename +
        ' -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 ./tmp_frames/frame%08d.jpg')


def fast_image_real_esrgan_animevideov3_x4_jpg_with_temp_folder():
    cmd('realesrgan-ncnn-vulkan.exe -i ./tmp_frames -o ./out_frames -n realesr-animevideov3-x4 -f jpg')


def fast_image_real_esrgan_animevideov3_x3_jpg_with_temp_folder():
    cmd('realesrgan-ncnn-vulkan.exe -i ./tmp_frames -o ./out_frames -n realesr-animevideov3-x3 -f jpg')


def fast_image_real_esrgan_animevideov3_x2_jpg_with_temp_folder():
    cmd('realesrgan-ncnn-vulkan.exe -i ./tmp_frames -o ./out_frames -n realesr-animevideov3-x2 -f jpg')


def hight_quality_image_real_esrgan_x4_plus_animevideo():
    cmd('realesrgan-ncnn-vulkan.exe -i ./tmp_frames -o ./out_frames -n realesrgan-x4plus-anime')


def reduce_image_size(image_path, output_folder, max_size_in_mb, max_size_in_px):
    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            width, height = image.size
            if width > max_size_in_px or height > max_size_in_px:
                scale = max_size_in_px / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = image.resize((new_width, new_height))

            output_path = os.path.join(
                output_folder, os.path.basename(image_path))
            quality = 95
            while True:
                image.save(output_path, format='JPEG', quality=quality)
                if os.stat(output_path).st_size <= max_size_in_mb * 1024 * 1024:
                    break
                quality -= 5
        return output_path
    except Exception as e:
        print('*_* ' + str(e))
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        if width > max_size_in_px or height > max_size_in_px:
            scale = max_size_in_px / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        output_path = os.path.join(
            output_folder, os.path.basename(image_path))
        temp_folder = './output/temp'
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        else:
            for filename in os.listdir(temp_folder):
                os.remove(os.path.join(temp_folder, filename))
        output_path = os.path.join(temp_folder, os.path.basename(image_path))
        cv2.imwrite(output_path, image)
        process_images_in_folder(
            temp_folder, './output/', max_size_in_mb, max_size_in_px)
        return output_path


def process_images_in_folder(folder_path, output_folder, max_size_in_mb, max_size_in_px):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.eps', '.gif',
                      '.ico', '.msp', '.pcx', '.ppm', '.spider', '.tif', '.tiff', '.xbm', '.xpm']
        if filename.endswith(tuple(extensions)):
            print(filename)
            image_path = os.path.join(folder_path, filename)
            reduce_image_size(image_path, output_folder,
                              max_size_in_mb, max_size_in_px)


def smaller_image():
    max_size_in_mb = float(
        input("Podaj ile MB nie może przekroczyć plik np.: 8: ") or 8)
    max_size_in_px = int(input(
        "Podaj długość największej krawędzi w px np.: 1024, 2048, 4096, 8192: ") or 4096)
    process_images_in_folder('./input/', './output/',
                             max_size_in_mb, max_size_in_px)


def frames_to_video_with_sound(filename, fps):
    # Połączenie ulepszonych klatek z powrotem w wideo, gdzie dźwięk zostanie skopiowany z pierwotnego wideo, nie obsługuje napisów
    # TRYB NORMALNY
    cmd('ffmpeg -r ' + fps + ' -i ./out_frames/frame%08d.jpg -i ./input/' + filename + ' -map 0:v:0? -map 1:a:0? -c:a copy -c:v libx264 -r ' +
        fps + ' -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 ./output/' + filename)

    # TRYB WALKI
    # cmd('ffmpeg -r ' + fps + ' -i ./out_frames/frame%08d.jpg -i ./input/' + filename + ' -map 0:v:0? -map 1:a:0? \
    # -filter_complex "[0:v]eq=contrast=1.1:brightness=-0.05:saturation=1.3,hqdn3d" \
    # -c:a copy -c:v libx264 -r ' + fps + ' -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 ./output/' + filename + '_TW.mp4')

    # TRYB SPORT
    # cmd('ffmpeg -r ' + fps + ' -i ./out_frames/frame%08d.jpg -i ./input/' + filename + ' -map 0:v:0? -map 1:a:0? \
    # -filter_complex "[0:v]eq=contrast=1.2:brightness=-0.1:saturation=1.5,hqdn3d" \
    # -c:a copy -c:v libx264 -r ' + fps + ' -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 ./output/' + filename + '_TS.mp4')

    # ŚCIĄGA:
    # TRYB ZWYKŁY -pix_fmt yuv420p
    # JAKOŚĆ I WIELKOŚĆ-crf 0 do 51, najwyższa jakość 0, najniższa jakość 51 (może powodować błędy w obrazie)
    # SZYBKOŚĆ I ODWROTNIE PROPORCJONALNA WIELKOSĆ -preset ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo (może powodować błędy w obrazie)
    # IDENTYCZNE KOLORY -color_primaries bt709 -color_trc bt709 -colorspace bt709
    # -filter_complex "[0:v]eq=contrast=1:brightness=1:saturation=1,hqdn3d" - filtry kolorów


def video_info():
    # Informacje o wideo
    filename = input("Podaj nazwę pliku np.: 1.mp4: ")
    cmd('ffmpeg -i ./input/' + filename)


def audio_with_image():
    input_dir = "./input"
    output_dir = "./output"
    image_path = os.path.join(
        input_dir, "0_src", os.listdir(os.path.join(input_dir, "0_src"))[0])

    for filename in os.listdir(input_dir):
        if filename.endswith(".mp3"):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(
                output_dir, os.path.splitext(filename)[0] + ".mp4")
            cmd('ffmpeg -loop 1 -i ' + image_path + ' -i ' +
                input_file_path + ' -c:a copy -shortest ' + output_file_path)
            print(f"Przetworzono plik {input_file_path}")
            time.sleep(1)


def add_subtitles():
    # Funkcja do wypalania napisów, konwertuje niedostępne czcionki na Arial w .ass
    filename = input("Podaj nazwę pliku głównego z napisami np.: 1.mkv: ")
    subfilename = input(
        "Podaj nazwę pliku napisów np.: 1.ass (bez fontów), 1.mkv: ")
    cmd('ffmpeg -i ./input/' + filename + ' -vf subtitles=./input/' + subfilename +
        ' -c:v libx264 -crf 10 -preset medium ./output/' + filename + '.mp4')

    # ŚCIĄGA:
    # TRYB ZWYKŁY -pix_fmt yuv420p
    # TRYB WALKI - usuń -pix_fmt yuv420p
    # JAKOŚĆ I WIELKOŚĆ-crf 0 - 51, najwyższa jakość 0, najniższa jakość 51
    # SZYBKOŚĆ I ODWROTNIE PROPORCJONALNA WIELKOSĆ -preset ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo


def add_lector():
    # Funkcja do dodawania lektora do filmu
    filename = input("Podaj nazwę pliku głównego z napisami np.: 1.mkv: ")
    lectorfilename = input("Podaj nazwę pliku lektora np.: 1.wav: ")
    cmd('ffmpeg -i ./input/' + filename + ' -i ./input/' + lectorfilename +
        ' -filter_complex "[1:a]volume=7dB[a1];[0:a][a1]amix=inputs=2:duration=first" -c:v libx264 -crf 10 -preset medium ./output/' + filename + '.mp4')

    # ŚCIĄGA:
    # TRYB ZWYKŁY -pix_fmt yuv420p
    # TRYB WALKI - usuń -pix_fmt yuv420p
    # JAKOŚĆ I WIELKOŚĆ-crf 0 - 51, najwyższa jakość 0, najniższa jakość 51
    # SZYBKOŚĆ I ODWROTNIE PROPORCJONALNA WIELKOSĆ -preset ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo


def add_subtitles_and_lector():
    # Połączenie napisów z lektorem, konwertuje niedostępne czcionki na Arial w .ass
    filename = input("Podaj nazwę pliku głównego z napisami np.: 1.mkv: ")
    subfilename = input(
        "Podaj nazwę pliku napisów np.: 1.ass (bez fontów), 1.mkv: ")
    lectorfilename = input("Podaj nazwę pliku lektora np.: 1.wav: ")
    cmd('ffmpeg -i ./input/' + filename + ' -i ./input/' + lectorfilename + ' -vf subtitles=./input/' + subfilename +
        ' -filter_complex "[1:a]volume=7dB[a1];[0:a][a1]amix=inputs=2:duration=first" -c:v libx264 -crf 10 -preset medium -b:a 256k -c:a aac -strict experimental -b:a 128k ./output/' + filename + '.mp4')

    # ŚCIĄGA:
    # TRYB ZWYKŁY -pix_fmt yuv420p
    # TRYB WALKI - usuń -pix_fmt yuv420p
    # JAKOŚĆ I WIELKOŚĆ-crf 0 - 51, najwyższa jakość 0, najniższa jakość 51
    # SZYBKOŚĆ I ODWROTNIE PROPORCJONALNA WIELKOSĆ -preset ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
    # ZGŁOŚNIENIE O X DECYBELI: volume=7dB


def merge_audio():
    # Łaczenie audio z filmu z lektorem
    # audiofilename1 = input(
    #     "Podaj nazwę pliku z dźwiękiem np.: 1.eac3, 1.aac: ")
    # audiofilename2 = input(
    #     "Podaj nazwę pliku z dźwiękiem lektora (+7db) np.: 1.wav: ")
    # cmd('ffmpeg -i ./input/' + audiofilename1 + ' -i ./input/' + audiofilename2 +
    #     ' -filter_complex "[1:a]volume=7dB[a1];[0:a][a1]amix=inputs=2:duration=first" ./output/' + audiofilename1 + '_' + audiofilename2 + '+7db.eac3')

    file_extension_1 = input(
        "Podaj rozszerzenie pliku z dźwiękiem np.: eac3, aac: ")
    filr_extension_2 = input(
        "Podaj rozszerzenie pliku z dźwiękiem lektora (+7db) np.: wav: ")
    for file in os.listdir('./input/'):
        if file.endswith(file_extension_1) and file[:-len(file_extension_1)] + filr_extension_2 in os.listdir('./input/'):
            cmd('ffmpeg -i ./input/' + file + ' -i ./input/' + file[:-len(file_extension_1)] + filr_extension_2 +
                ' -filter_complex "[1:a]volume=7dB[a1];[0:a][a1]amix=inputs=2:duration=first" ./output/' + file + '_' + file[:-len(file_extension_1)] + filr_extension_2 + '+7db.eac3')

    # ŚCIĄGA:
    # ZGŁOŚNIENIE O X DECYBELI: volume=7dB


def main():
    start_time = time.time()
    # red green yellow white attrs=['bold']
    cprint("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝",
           'white', attrs=['bold'])
    cprint("")
    cprint("Wybierz jedną z poniższych opcji:")
    cprint("1. Ulepsz i skaluj zdjęcia Real-ESRGAN")
    cprint("2. Zmniejszanie rozmiaru w MB i px")
    cprint("3. Ulepsz i skaluj anime / film")
    cprint("4. Wyświetl informacje o pliku wideo lub audio")
    cprint("5. Konwertuj audio i obraz do wideo")
    cprint("6. Wypal napisy do wideo")
    cprint("7. Dodaj ścieżkę dźwiękową lektora do wideo")
    cprint("8. Wypal napisy i dodaj ścieżkę dźwiękową lektora do wideo")
    cprint("9. Nałóż na siebie dwie ścieżki dźwiękowe")

    choice = input("Wybierz numer opcji: ")

    if choice == '1':
        # hight_quality_image_real_esrgan_x4_plus_anime()
        # fast_image_real_esrgan_animevideov3_x4()
        # fast_image_real_esrgan_animevideov3_x4_jpg()
        # slow_image_real_esrgan_x4_plus()

        print("Wybierz jedną z poniższych opcji:")
        print("1. hight_quality_image_real_esrgan_x4_plus_anime - Model do anime artów")
        print("2. fast_image_real_esrgan_animevideov3_x4 - Gorszy model do anime artów")
        print("3. fast_image_real_esrgan_animevideov3_x4_jpg - Szybki, model do anime artów, gorsza jakość")
        print(
            "4. slow_image_real_esrgan_x4_plus - Wolny model do wszylkiego rodzaju obrazów")
        model = input("Wybierz numer opcji: ")

        if model == '1':
            hight_quality_image_real_esrgan_x4_plus_anime()

        if model == '2':
            fast_image_real_esrgan_animevideov3_x4()

        if model == '3':
            fast_image_real_esrgan_animevideov3_x4_jpg()

        if model == '4':
            slow_image_real_esrgan_x4_plus()

    if choice == '2':
        smaller_image()

    if choice == '3':
        filename, fps = add_info()
        video_to_frames(filename)

        # fast_image_real_esrgan_animevideov3_x4_jpg_with_temp_folder()  # 8K
        # fast_image_real_esrgan_animevideov3_x3_jpg_with_temp_folder()  # 4K
        # fast_image_real_esrgan_animevideov3_x2_jpg_with_temp_folder()  # 2K
        # hight_quality_image_real_esrgan_x4_plus_animevideo()  # 8K high quality slow

        print("Wybierz jedną z poniższych opcji:")
        print("1. fast_image_real_esrgan_animevideov3_x4_jpg_with_temp_folder - Anime 1080p -> 4K")
        print("2. fast_image_real_esrgan_animevideov3_x3_jpg_with_temp_folder - Anime 1080p -> 3K")
        print("3. fast_image_real_esrgan_animevideov3_x2_jpg_with_temp_folder - Anime 1080p -> 2K")
        print("4. hight_quality_image_real_esrgan_x4_plus_animevideo - Film 1080p -> 8K, bardzo, bardzo wolno")
        model = input("Wybierz numer opcji: ")

        if model == '1':
            fast_image_real_esrgan_animevideov3_x4_jpg_with_temp_folder()

        if model == '2':
            fast_image_real_esrgan_animevideov3_x3_jpg_with_temp_folder()

        if model == '3':
            fast_image_real_esrgan_animevideov3_x2_jpg_with_temp_folder()

        if model == '4':
            hight_quality_image_real_esrgan_x4_plus_animevideo()

        frames_to_video_with_sound(filename, fps)
        # clean()

    if choice == '4':
        video_info()

    if choice == '5':
        audio_with_image()

    if choice == '6':
        add_subtitles()

    if choice == '7':
        add_lector()

    if choice == '8':
        add_subtitles_and_lector()

    if choice == '9':
        merge_audio()

    # Mierz czas
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %s minutes ---" % ((time.time() - start_time) / 60))
    print("--- %s hours ---" % ((time.time() - start_time) / 3600))


if __name__ == "__main__":
    main()
