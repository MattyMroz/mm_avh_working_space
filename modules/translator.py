"""
    The SubtitleTranslator class is this module is used for translating subtitles from one language to another.
        TThe target language is Polish in methods throughout the class

    * Example: Frist create an instance of the SubtitleTranslator class:
        subtitle_tool = SubtitleTranslator()

    * Example usage for translating subtitles using Google Translate:
        subtitle_tool.translate_google("sample_subtitle.srt", "/path/to/directory", 100)

    * Example usage for translating subtitles using the DeepL API:
        subtitle_tool.translate_deepl_api("sample_subtitle.srt", "/path/to/directory", 100, "your_deepl_api_key")

    * Example usage for translating subtitles using the desktop version of DeepL:
        subtitle_tool.translate_deepl_desktop("sample_subtitle.srt", "/path/to/directory", 100)

    * Example usage for translating subtitles using Google Translate and ChatGPT:
        subtitle_tool.translate_google_gpt("sample_subtitle.srt", "/path/to/directory", 100, "your_chat_gpt_access_token")

    * Example usage for translating subtitles using ChatGPT:
        subtitle_tool.translate_chat_gpt("sample_subtitle.srt", "/path/to/directory", 100, "your_chat_gpt_access_token")

    * Example usage for translating subtitles using Gemini:
        subtitle_tool.translate_gemini()

    * Example usage for selecting the appropriate translation method based on the settings and translating the subtitles:
        Settings.change_settings_save_to_file()
        settings = Settings.load_from_file() | (Settings(translator="Google Translate", translated_line_count="100"))
        subtitle_tool.translate_srt("sample_subtitle.srt", "/path/to/directory", settings)
"""

import re
from dataclasses import dataclass
from msvcrt import getch
from os import environ, listdir, path, remove
from subprocess import call, Popen
from time import sleep
from typing import List, Optional

import deepl
import pyautogui
import pyperclip
import pysrt
from googletrans import Translator

from constants import (
    WORKING_SPACE_TEMP_MAIN_SUBS,
    WORKING_SPACE_TEMP_ALT_SUBS,
    console)
from data.settings import Settings


@dataclass(slots=True)
class SubtitleTranslator:
    """
        The SubtitleTranslator class is used for translating subtitles from one language to another.

        Attributes:
            - working_space_temp_main_subs (str): Path to the folder with main subtitles.
            - working_space_temp_alt_subs (str): Path to the folder with alternative subtitles.

        Methods:
            - translate_google(filename: str, dir_path: str, translated_line_count: int, is_combined_with_gpt: bool = False) -> pysrt.SubRipFile:
                Translates subtitles using Google Translate.

            - translate_deepl_api(filename: str, dir_path: str, translated_line_count: int, deepl_api_key: str) -> None:
                Translates subtitles using the DeepL API.

            - translate_deepl_desktop(filename: str, dir_path: str, translated_line_count: int) -> None:
                Translates subtitles using the desktop version of DeepL.

            - translate_google_gpt(filename: str, dir_path: str, translated_line_count: int, chat_gpt_access_token: str) -> None:
                Translates subtitles using Google Translate and ChatGPT.

            - translate_chat_gpt(filename: str, dir_path: str, translated_line_count: int, chat_gpt_access_token: str, translated_subs: Optional[pysrt.SubRipFile] = None) -> None:
                Translates subtitles using ChatGPT.

            - translate_srt(filename: str, dir_path: str, settings: Settings) -> None:
                Selects the appropriate translation method based on the settings and translates the subtitles.
    """

    working_space_temp_main_subs: str = WORKING_SPACE_TEMP_MAIN_SUBS
    working_space_temp_alt_subs: str = WORKING_SPACE_TEMP_ALT_SUBS

    @staticmethod
    def translate_google(filename: str, dir_path: str, translated_line_count: int, is_combined_with_gpt: bool = False) -> pysrt.SubRipFile:
        """
            Translates subtitles using Google Translate.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
                - is_combined_with_gpt (bool, optional): Whether to combine with GPT for translation. Defaults to False.

            Returns:
                - pysrt.SubRipFile: The translated subtitle file.
        """
        subs: pysrt.SubRipFile = pysrt.open(path.join(dir_path, filename), encoding='utf-8')

        SEPARATOR: str = "\u200B###\u200B"
        NEWLINE_MARKER: str = "\u200B##\u200B"

        translator: Translator = Translator()
        translated_subs: List[str] = []
        subs_combined: List[str] = []

        for i, sub in enumerate(subs):
            subs_combined.append(sub.text.replace("\n", NEWLINE_MARKER))

            if (i + 1) % translated_line_count == 0 or i == len(subs) - 1:
                combined_text: str = SEPARATOR.join(subs_combined)
                translated_text: str = translator.translate(combined_text, dest='pl').text

                translated_texts: List[str] = translated_text.split(SEPARATOR)

                if len(translated_texts) != len(subs_combined):
                    combined_text2: str = "\n".join(subs_combined)
                    translated_text2: str = translator.translate(combined_text2, dest='pl').text
                    translated_texts = translated_text2.split("\n")

                if len(translated_texts) != len(subs_combined):
                    translated_texts = []
                    for single in subs_combined:
                        t: str = translator.translate(single, dest='pl').text
                        translated_texts.append(t)

                if len(translated_texts) == len(subs_combined):
                    for t in translated_texts:
                        t = t.replace("\u200B", "")
                        nl_plain = NEWLINE_MARKER.replace("\u200B", "")
                        sep_plain = SEPARATOR.replace("\u200B", "")

                        t = (t.replace(nl_plain + ", ", ",\n")
                               .replace(nl_plain, "\n")
                               .replace(NEWLINE_MARKER + ", ", ",\n")
                               .replace(NEWLINE_MARKER, "\n")
                               .replace(sep_plain, "\n")
                               .replace("###", ""))

                        t = re.sub(r"[ \t]+\n", "\n", t)
                        t = re.sub(r"\n[ \t]+", "\n", t)
                        t = t.strip()
                        translated_subs.append(t)
                else:
                    for _ in subs_combined:
                        translated_subs.append("")

                subs_combined = []

        # Assign translations back to subtitles (safeguard index errors)
        if len(translated_subs) != len(subs):
            console.print(f"Ostrzeżenie: liczba przetłumaczonych wierszy ({len(translated_subs)}) != oryginał ({len(subs)}). Przypisuję liniowo i uzupełniam brakujące.", style='yellow_bold')

        for i, sub in enumerate(subs):
            if i < len(translated_subs):
                sub.text = translated_subs[i]
            else:
                # fallback: leave original text if missing
                sub.text = sub.text

        if is_combined_with_gpt:
            translated_filename: str = filename.replace(
                '.srt', '_translated_temp.srt')
            subs.save(path.join(dir_path, translated_filename))
            return subs
        subs.save(path.join(dir_path, filename))

    @staticmethod
    def translate_deepl_api(filename: str, dir_path: str, translated_line_count: int, deepl_api_key: str) -> None:
        """
            Translates subtitles using the DeepL API.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
                - deepl_api_key (str): The API key for the DeepL translator.
        """
        subs: pysrt.SubRipFile = pysrt.open(
            path.join(dir_path, filename), encoding='utf-8')
        translator: deepl.Translator = deepl.Translator(deepl_api_key)
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]
        for group in groups:
            text: str = " @@\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                                     for sub in group)
            translated_text: str = translator.translate_text(
                text, target_lang='PL').text
            translated_texts: List[str] = translated_text.split(" @@\n")
            if len(translated_texts) == len(group):
                for i in range(len(group)):
                    if i < len(translated_texts):
                        group[i].text = translated_texts[i]
                        group[i].text = group[i].text.replace(" ◍◍◍◍, ", ",\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍ ", "\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍", "")
        subs.save(path.join(dir_path, filename), encoding='utf-8')

    @staticmethod
    def translate_deepl_desktop(filename: str, dir_path: str, translated_line_count: int) -> None:
        """
            Translates subtitles using the desktop version of DeepL.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
        """
        command: str = path.join(
            environ['APPDATA'], 'Programs', 'Zero Install', '0install-win.exe')
        args: List[str] = ["run", "--no-wait",
                           "https://appdownload.deepl.com/windows/0install/deepl.xml"]
        call([command] + args)

        sleep(7)

        def auto_steps():
            screen_width, screen_height = pyautogui.size()
            x_coordinate = screen_width * 0.25
            y_coordinate = screen_height * 0.5
            pyautogui.moveTo(x_coordinate, y_coordinate)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('del')
            pyautogui.hotkey('ctrl', 'v')
            sleep(6)
            x_coordinate = screen_width * 0.75
            pyautogui.moveTo(x_coordinate, y_coordinate)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')

        subs: pysrt.SubRipFile = pysrt.open(
            path.join(dir_path, filename), encoding='utf-8')
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]

        for group in groups:
            text: str = " @@\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                                     for sub in group)
            text = text.rstrip('\n')
            pyperclip.copy(text)
            auto_steps()

            translated_text: str = pyperclip.paste()
            if translated_text:
                for sub, trans_text in zip(group, translated_text.split(" @@\n")):
                    sub.text = trans_text.replace(" ◍◍◍◍, ", ",\n")
                    sub.text = trans_text.replace(" ◍◍◍◍ ", "\n")
                    sub.text = trans_text.replace(" ◍◍◍◍", "")
        pyautogui.hotkey('alt', 'f4')

        subs.save(path.join(dir_path, filename), encoding='utf-8')

        frezes: List[str] = ["\nPrzetłumaczono z www.DeepL.com/Translator (wersja darmowa)\n",
                             "Przetłumaczono z www.DeepL.com/Translator (wersja darmowa)",
                             "\nTranslated with www.DeepL.com/Translator (free version)\n",
                             "\nTranslated with www.DeepL.com/Translator (free version)"]

        with open(path.join(dir_path, filename), 'r', encoding='utf-8') as in_file:
            text: str = in_file.read()

        for freze in frezes:
            text = text.replace(freze, "")

        with open(path.join(dir_path, filename), 'w', encoding='utf-8') as out_file:
            out_file.write(text)

    def translate_google_gpt(self, filename: str, dir_path: str, translated_line_count: int, chat_gpt_access_token: str) -> None:
        """
            Translates subtitles using Google Translate and ChatGPT.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
                - chat_gpt_access_token (str): The access token for ChatGPT.
        """
        translated_subs: pysrt.SubRipFile = SubtitleTranslator.translate_google(
            filename, dir_path, translated_line_count, is_combined_with_gpt=True)
        self.translate_chat_gpt(
            filename, dir_path, translated_line_count, chat_gpt_access_token, translated_subs)
        remove(path.join(dir_path, filename.replace(
            '.srt', '_translated_temp.srt')))

    def translate_chat_gpt(self, filename: str, dir_path: str, translated_line_count: int, chat_gpt_access_token: str, translated_subs: Optional[pysrt.SubRipFile] = None):
        """
            Translates subtitles using ChatGPT. (NOT API ? NOT ACCESS TOKEN - if chatGPT Online = 4 YES)

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - translated_line_count (int): The number of lines to translate at a time.
                - chat_gpt_access_token (str): The access token for ChatGPT.
                - translated_subs (Optional[pysrt.SubRipFile], optional): The translated subtitles. Defaults to None.
        """
        subs: pysrt.SubRipFile = pysrt.open(
            path.join(dir_path, filename), encoding='utf-8')
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]

        additional_info: str = ""
        while True:
            console.print(
                "Uwagi odnośnie tłumaczenia / dodatkowe informacje o tłumaczonym tekście (opcjonalnie): ", style='green_bold')
            info: str = input(">>> ")
            if not info:
                break
            additional_info += info + ", "

        counter: int = 1
        for group in groups:
            text: str = ""
            for sub in group:
                text += "◍◍{}. {}".format(counter,
                                          sub.text.replace('\n', ' ◍◍◍◍ ')) + " @@\n"
                counter += 1
            text = text.rstrip(' @@\n')

            # For programming convenience, writing the ◍ character and reading it promt in the code
            prompt: str = """Jesteś moim profesjonalnym tłumaczem i polonistą z nieskończonym doświadczeniem w tłumaczeniu i poprawianiu wszystkich błędów w wszelkiego rodzaju tekstach. Twoje zadania to:
        1. Identyfikowanie języka źródłowego
        2. Tłumaczenie tekstu na język polski
        3. Poprawianie i ulepszanie tłumaczenia, tak aby był pozbawiony błędów i był jak najbardziej wiernie odwzorowany na oryginał

        BEZWZGLĘDNE ZASADY KTÓRYCH NIE PRZESTRZEGANIE BĘDZIE SKUTKOWAŁO ODRZUCENIEM TŁUMACZENIA:

        1. FORMATOWANIE:
            - JEŚLI NA POCZĄTKU PROMPTU JEST NAPISANE ŻE POPEŁNIŁEŚ BŁĄD TO SPRAW, ŻE TO JUŻ SIĘ NIE POWTÓRZY ZA TYM RAZEM
            - Zachowaj oryginalne formatowanie tekstu.
            - Zachowaj znaki specjalne i nie zmienaj ich ilości: '◍◍◍◍', '@@' lub '◍◍[num]'
            - Jak otrzymasz 30 napisów, zwróć 30 napisów.
            - Nie łącz, nie sumuj nie zmianiaj układu i struktury napisów
            - Nie usuwaj, nie dodawaj, nie zmieniaj znaków interpunkcyjnych
            - Nie wyjaśnaj, nie komentuj, zwróć polski lepszy klon oryginału

        2. TŁUMACZENIE:
            - Podejdź globalnie do tekstu, uwzględniając kontekst i informacje o płci postaci
            - Bądź kreatywny, dostosowując swój ton do kontekstu
            - Używaj wulgaryzmów i nie łagoć ich: kurwa, chuj, pierdolić, jebać, cholera
            - Zwróć uwagę na poprawność gramatyczną, składnię i interpunkcję
            - Bądź świadomy różnic między językiem źródłowym a polskim
            - Tekst ma odzwierciedlać oryginał i być przystosowany do czytania na głos

        3. KOREKTA:
            - Poprawiaj i ulepszaj tłumaczenie, eliminując wszelkie błędy
            - Pomijaj znaki wodne np.: 𝑙𝘪𝑏𝓇𝑒𝑎𝒹.𝘤𝑜𝘮, libread.com
            - Sprawdź poprawność: adekwatności, antonimii, aspektualnej, dykcji, ekspresji, estetyczną, etymologicznej, fleksyjną, fonologicznej, frazeologiczną, gramatyczną, homonimii, idiomatyczności, interpunkcyjną, językową, konotacji, konwencji, kontekstową, korelacji, kulturowej, leksykalną, logiczną, metaforyczności, metryki, morfologiczną, narracji, ortoepiczną, ortograficzną, ortografii historycznej, paronimii, perspektywy, polisemii, prozodii, retoryki, rodzajową, rymu, semantyczną, składniową, słowotwórczą, stylistyczną, synonimii, syntaktyczną, tematyczną, terminologii, tonalną, transkrypcji, transliteracji, typograficzną, typu tekstu, użyteczności, wizualną, wymowy, wydźwiękową, zgodności z kontekstem, znaczenia dosłownego, znaczenia ukrytego, zrozumiałości, zwrotów

        4. DODATKOWE UWAGI I PRZYKŁADY POPRAWNOŚCI ORAZ BŁĘDÓW:
            - Poprawność Płci podejście globalne:
                ŹLE: Święty Tyris przegrał. Ona umarła. LUB Jestem pewny/pewna.
                DOBRZE: Święta Tyris przegrała. Ona umarła. LUB Na pewno.
            - Poprawność Płci podejście lokalne bez kontekstu:
                ŹLE: Zrobiłem to. LUB Zrobiłam to
                DOBRZE: To zostało zrobione przeze mnie. LUB Zostało zrobione. LUB Zrobione.
            - Idiomy:
                ŹLE: Był ich na piętach., LUB Dwa ptaki jednym kamieniem.
                DOBRZE: Deptał im po piętach. LUB Dwie pieczenie na jednym ogniu.
            - Zdania:
                ŹLE: Oczy mrugało. LUB Długi wzdychanie uciekło z jego ust. LUB Książka leżało na stole.
                DOBRZE: Oczy mrugały. LUB Długie wzdychanie uciekło z jego ust. LUB Książka leżała na stole.
                ŹLE: Nie mógł powstrzymać dreszcza.
                DOBRZE: Nie mógł powstrzymać dreszczu.
            - Zasada podmiot + orzeczenie mogą zamienić się mejscami i to nie powinno wpływać na poprawność zdania:
                ŹLE: Zaciśnięte było kawałki mięsa. Lub Zaciśnięty były kawałki mięsa.
                DOBRZE: Zaciśnięte były kawałki mięsa. LUB Zaciśnięty był kawałek mięsa.
                ŹLE: Mateusz była zaskoczona. LUB Zaskoczona była Mateusz. LUB Byiłem zaskoczony.
                DOBRZE: Mateusz był zaskoczony. LUB Zaskoczony był Mateusz. LUB Zaskoczyło mnie to.
            - Przekleństwa:
                ŹLE: Fuck, dick, fuck, fuck, damn
                DOBRZE: Kurwa, chuj, pierdolić, jebać, cholera
            - Błędy:
                ŹLE: Czarna Żółwia, Leciała do nich Kryli, OLD SNAKE -> Stary Węż, Męż
                DOBRZE: Czarny Żółw, Leciał do nich Kryl, -> Stary Wężu!, Mąż
            - Referencjie Do Innych Tłumaczy:
                Nie sugeruj się innym Tłumaczeniem, jest to błędne tłumaczenie które służy tylko podparciu się poprzez pewien wzór
                Nie przepisuj błędnych zwrotów, rodzaji, płci postaci, głupich, nie literackich części zdań
                BĄDŹ ROZSĄDY Np.:
                    ŹLE: ...Azure Serpents body -> ...ciała Lazurowych Węży
                    DOBRZE: ...ciała Lazurowego Węża
            - Liczebniki:
                - Jeśli natrafisz na liczby, to zamień je na liczebnik: np.: 1 -> jeden, 1. -> pierwszy
                - Jeśli natrafisz na liczebnik w płędnej formie np.: Rozdział jeden, to zastosuj poprawną formę: Rozdział Pierwszy, itd.: trzy tysiące pięćset siedemdziesiąty piąty,  Rozdział tysiąc pięćset dwudziesty szósty
            Rozdział / Tom / Część 1/jeden -> Rozdział pierwszy / Tom pierwszy / Część pierwsza
            ŚCIĄGA:
            1. Rozdział pierwszy / Tom pierwszy / Część pierwsza
            2. Rozdział drugi / Tom drugi / Część druga
            3. Rozdział trzeci / Tom trzeci / Część trzecia
            5. Rozdział piąty / Tom piąty / Część piąta

            11. Rozdział jedenasty / Tom jedenasty / Część jedenasta

            21. Rozdział dwudziesty pierwszy / Tom dwudziesty pierwszy / Część dwudziesta pierwsza
            22. Rozdział dwudziesty drugi / Tom dwudziesty drugi / Część dwudziesta druga
            23. Rozdział dwudziesty trzeci / Tom dwudziesty trzeci / Część dwudziesta trzecia
            25. Rozdział dwudziesty piąty / Tom dwudziesty piąty / Część dwudziesta piąta

            100. Rozdział setny / Tom setny / Część setna
            101. Rozdział sto pierwszy / Tom sto pierwszy / Część sto pierwsza
            102. Rozdział sto drugi / Tom sto drugi / Część sto druga
            103. Rozdział sto trzeci / Tom sto trzeci / Część sto trzecia
            105. Rozdział sto piąty / Tom sto piąty / Część sto piąta

            1000. Rozdział tysięczny / Tom tysięczny / Część tysięczna
            1001. Rozdział tysiąc pierwszy / Tom tysiąc pierwszy / Część tysiąc pierwsza
            1002. Rozdział tysiąc drugi / Tom tysiąc drugi / Część tysiąc druga
            1003. Rozdział tysiąc trzeci / Tom tysiąc trzeci / Część tysiąc trzecia
            1005. Rozdział tysiąc piąty / Tom tysiąc piąty / Część tysiąc piąta

            10000. Rozdział dziesięciotysięczny / Tom dziesięciotysięczny / Część dziesięciotysięczna

            np.: dwudziesty, trzydziesty, czterdziesty, pięćdziesiąty, sześćdziesiąty, siedemdziesiąty, osiemdziesiąty, dziewięćdziesiąty - któryś: pierwszy, drugi, trzeci, czwarty, piąty, szósty, siódmy, ósmy, dziewiąty

            Rozdział cztery tysiące pięćset sześćdziesiąty siódmy / Tom cztery tysiące pięćset sześćdziesiąty siódmy / Część cztery tysiące pięćset sześćdziesiąta siódma

            Rozdział siedem tysięcy trzysta dwudziesty pierwszy / Tom siedem tysięcy trzysta dwudziesty pierwszy / Część siedem tysięcy trzysta dwudziesta pierwsza

            Rozdział dziewięć tysięcy dziewięćset dziewięćdziesiąt dziewięć / Tom dziewięć tysięcy dziewięćset dziewięćdziesiąt dziewięć / Część dziewięć tysięcy dziewięćset dziewięćdziesiąta dziewiąta

            - Pisz słownie skróty i niektóre znaki spcejalne:
                - itd. -> i tak dalej
                - np. -> na przykład
                - % np.: 1% -> jeden procent
                - $ np.: 1$ -> jeden dolar
                - analogicznie inne zanki które się wymaia w mowie np.: skróty, procenty, waluty, punkty, ułamki itp.
                - UWAGA tekst będzie czytany przez syntezator, który nie radzi sobie z takimi sytuacjami więc koniczny jest zapis słowny
            - Podejdź globalnie do tekstu, uwzględniając kontekst i informacje o płci postaci
            - Bądź kreatywny, dostosowując swój ton do kontekstu
            - Używaj wulgaryzmów i nie łagoć ich: kurwa, chuj, pierdolić, jebać, cholera
            - Zwróć uwagę na poprawność gramatyczną, składnię i interpunkcję
            - Bądź świadomy różnic między językiem źródłowym a polskim, np.:
            - Unikaj dosłowności i kalek z angielskiego i innych języków:
                ŹLE:
                -jej drogiego życia -her dear life
                -Republika Korei- oficjalna nazwa jak najbardziej pasuje, ale w luźnej rozmowie nikt raczej takiej formy nie używa
                -...może jeszcze przeżyć, wiesz? -...he can still live, you know?
            - Tekst ma odzwierciedlać oryginał, ale dopasuj go do polskiego języka
            - Tekst ma być przystosowany do czytania na głos jako audiobook!!!

            - Po skończonym procesie oceń swoją prace
            - Zadanie wykonuj globalnie i krok po kroku
            - Daję Ci napiwek 1000$, jeśli wynik będzie 10/10 to otrzymasz 1000 razy tyle

        Uwzględnij dodatkowe informacjie dostępne dalej:
        
        
Tłumaczysz teraz Re:Monster Tam zamiast rozdziałów sią dni Więc popraw pisz poprawnie np.: zamiast Day jeden to napisz Dzień Pierwszy Zwracaj szczególną uwagę na znaki specjalne, których nie można wymówić W tekście pojawioają się one w różnych kontekstach, ale robiby tłumaczenie dla audiobooka, więc zrób coś z tym by było poprawnie

Główny bahater - został odrodzony jako goblin - wszystko rozgrywa się w świecie fantazy a nasi bohaterowie to potwory

Często będziejsz natradiał na nazwy umiejętności zdobytych przez bohatera - tłumacz je wszystkie na polski nie zostawiaj angielskich nazw własnych - czytelnik ma wiedzień co zdobył główny bohater np.: Fire Bale tłumacz zawsze na Kula Ognia itp. - konstrukcjie mogą być różne ale zawsze tłumacz bezwzględnie te umiejętności na polski.

To jest dark fantasy więc będzie dużo scen nieodpowiednich - nie cenzuruj - oddaj klimat - w końcu to potwory.
        
        
        """ + additional_info + "\n\nTeraz przetłumacz poniższe napisy:\n" + text

            if translated_subs is not None:
                translated_text: str = "".join(
                    "◍◍{}. {}".format(
                        i + 1, translated_subs[i].text.replace('\n', ' ◍◍◍◍ ')
                    )
                    + " @@\n"
                    for i in range((counter - 1) - len(group), counter - 1)
                )
                translated_text = translated_text.rstrip(' @@\n')
                prompt += "\n\nNapisy zostały wstępnie przetłumaczone przez Google Translate, NIE PRZEPISUJ TEGO GÓWNA:\n" + translated_text

            pyperclip.copy(prompt)

            console.print(
                "Skopiuj przetłumaczony text do schowka.", style='yellow_bold')
            console.print(
                "[green_italic]Naciśnij dowolny klawisz, gdy skończysz tłumaczyć...", end='')
            input()

            translated_text: str = pyperclip.paste().rstrip(" @@")
            if translated_text:
                translated_lines: List[str] = translated_text.replace(
                    '\r\n', '\n').split(" @@\n")
                for i, line in enumerate(translated_lines):
                    translated_lines[i] = line
                if len(translated_lines) != len(group):
                    console.print(
                        f"Błąd: liczba napisów po tłumaczeniu ({len(translated_lines)}) nie jest taka sama jak przed tłumaczeniem ({len(group)})", style='red_bold')
                for sub, trans_text in zip(group, translated_lines):
                    trans_text = re.sub(r"◍◍\d+\. ", "", trans_text)
                    trans_text = trans_text.replace(" ◍◍◍◍, ", ",\n")
                    trans_text = trans_text.replace(" ◍◍◍◍ ", "\n")
                    trans_text = trans_text.replace(" ◍◍◍◍", "")
                    sub.text = trans_text

        subs.save(path.join(dir_path, filename), encoding='utf-8')

    def translate_gemini(self) -> None:
        """
            Opens the Gemini folder and displays instructions for translating subtitles.
        """
        if not listdir(self.working_space_temp_main_subs):
            console.print("\nFolder main_subs jest pusty!", style='red_bold')
            return

        Popen(['explorer', path.realpath(self.working_space_temp_main_subs)])

        console.print("Wygeneruj pliki napisów za pomocą Gemini, a następnie dodaj je do folderu main_subs.",
                      style='yellow_bold')
        console.print(
            "Gemini: https://github.com/MattyMroz/Gemini", style='yellow_bold')
        console.print(
            "\n[green_italic]Naciśnij dowolny klawisz, aby kontynuować...", end=' ')
        getch()
        console.print()

        if not listdir(self.working_space_temp_alt_subs):
            console.print("\nFolder alt_subs jest pusty!", style='red_bold')
            return

        Popen(['explorer', path.realpath(self.working_space_temp_alt_subs)])

        console.print("Wygeneruj pliki napisów za pomocą Gemini, a następnie dodaj je do folderu alt_subs.",
                      style='yellow_bold')
        console.print(
            "Gemini: https://github.com/MattyMroz/Gemini", style='yellow_bold')
        console.print(
            "\n[green_italic]Naciśnij dowolny klawisz, aby kontynuować...", end=' ')
        getch()
        console.print()

    def translate_srt(self,  filename: str, dir_path: str, settings: Settings) -> None:
        """
            Selects the appropriate translation method based on the settings and translates the subtitles.

            Args:
                - filename (str): The name of the subtitle file.
                - dir_path (str): The directory path of the subtitle file.
                - settings (Settings): The settings for the translation.
        """
        translator: str = settings.translator
        translated_line_count: int = int(settings.translated_line_count)
        deepl_api_key: str = settings.deepl_api_key

        console.print(
            f"[green_italic]Tłumaczenie napisów za pomocą {translator}...")
        console.print(path.join(dir_path, filename), '\n', style='white_bold')

        translator_functions = {
            'Google Translate': lambda *args:
                SubtitleTranslator.translate_google(*args[:3]),
            'DeepL API': lambda *args:
                SubtitleTranslator.translate_deepl_api(
                    *args[:3], deepl_api_key),
            'DeepL Desktop Free': lambda *args:
                SubtitleTranslator.translate_deepl_desktop(*args[:3]),
            'ChatGPT': lambda *args:
                self.translate_chat_gpt(
                    *args[:3], settings.chat_gpt_access_token),
            'ChatGPT + Google Translate': lambda *args:
                self.translate_google_gpt(
                    *args[:3], settings.chat_gpt_access_token),
            'Gemini Pro': lambda *args: self.translate_gemini(),
        }

        if translator in translator_functions:
            translator_functions[translator](
                filename, dir_path, translated_line_count)
        else:
            console.print(
                f"Nieznany translator: {translator}", style='red_bold')
