from dataclasses import dataclass
from typing import Optional, List
import os
import pysrt
from googletrans import Translator
import deepl
import pyautogui
import pyperclip
import time
import subprocess
from rich.theme import Theme
from rich.console import Console
from data.settings import Settings
from revChatGPT.V1 import Chatbot
import re


@dataclass(slots=True)
class SubtitleTranslator:
    translator: Optional[str] = None
    deepl_api_key: Optional[str] = None
    translated_line_count: Optional[str] = None

    console: Console = Console(theme=Theme({"repr.number": "bold red"}))

    @staticmethod
    def translate_google(filename: str, dir_path: str, translated_line_count: int, is_combined_with_gpt: bool = False) -> pysrt.SubRipFile:
        subs: pysrt.SubRipFile = pysrt.open(
            os.path.join(dir_path, filename), encoding='utf-8')
        subs_combined: List[str] = []
        translated_subs: List[str] = []

        translator: Translator = Translator()
        for i, sub in enumerate(subs):
            sub.text = sub.text.replace("\n", " ◍ ")
            subs_combined.append(sub.text)

            if (i + 1) % translated_line_count == 0 or i == len(subs) - 1:
                combined_text: str = "\n".join(subs_combined)
                translated_text: str = translator.translate(
                    combined_text, dest='pl').text
                translated_subs += translated_text.split("\n")
                subs_combined = []

        for i, sub in enumerate(subs):
            sub.text = translated_subs[i]
            sub.text = sub.text.replace(" ◍, ", ",\n")
            sub.text = sub.text.replace(" ◍ ", "\n")
            sub.text = sub.text.replace(" ◍", "")

        if is_combined_with_gpt:
            translated_filename: str = filename.replace(
                '.srt', '_translated_temp.srt')
            subs.save(os.path.join(dir_path, translated_filename))
            return subs
        else:
            subs.save(os.path.join(dir_path, filename))

    @staticmethod
    def translate_deepl_api(filename: str, dir_path: str, translated_line_count: int, deepl_api_key: str):
        subs: pysrt.SubRipFile = pysrt.open(
            os.path.join(dir_path, filename), encoding='utf-8')
        translator: deepl.Translator = deepl.Translator(deepl_api_key)
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]
        for group in groups:
            text: str = " @\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                                    for sub in group)
            translated_text: str = translator.translate_text(
                text, target_lang='PL').text
            translated_texts: List[str] = translated_text.split(" @\n")
            if len(translated_texts) == len(group):
                for i in range(len(group)):
                    if i < len(translated_texts):
                        group[i].text = translated_texts[i]
                        group[i].text = group[i].text.replace(" ◍◍◍◍, ", ",\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍ ", "\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍", "")
        subs.save(os.path.join(dir_path, filename), encoding='utf-8')

    @staticmethod
    def translate_deepl_desktop(filename: str, dir_path: str, translated_line_count: int):
        command: str = os.path.join(
            os.environ['APPDATA'], 'Programs', 'Zero Install', '0install-win.exe')
        args: List[str] = ["run", "--no-wait",
                           "https://appdownload.deepl.com/windows/0install/deepl.xml"]
        subprocess.call([command] + args)

        time.sleep(7)

        def auto_steps():
            screen_width, screen_height = pyautogui.size()
            x = screen_width * 0.25
            y = screen_height * 0.5
            pyautogui.moveTo(x, y)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('del')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(6)
            x = screen_width * 0.75
            pyautogui.moveTo(x, y)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')

        subs: pysrt.SubRipFile = pysrt.open(
            os.path.join(dir_path, filename), encoding='utf-8')
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]

        for group in groups:
            text: str = " @\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                                    for sub in group)
            text = text.rstrip('\n')
            pyperclip.copy(text)
            auto_steps()

            translated_text: str = pyperclip.paste()
            if translated_text:
                for sub, trans_text in zip(group, translated_text.split(" @\n")):
                    sub.text = trans_text.replace(" ◍◍◍◍, ", ",\n")
                    sub.text = trans_text.replace(" ◍◍◍◍ ", "\n")
                    sub.text = trans_text.replace(" ◍◍◍◍", "")
        pyautogui.hotkey('alt', 'f4')

        subs.save(os.path.join(dir_path, filename), encoding='utf-8')

        frezes: List[str] = ["\nPrzetłumaczono z www.DeepL.com/Translator (wersja darmowa)\n",
                             "Przetłumaczono z www.DeepL.com/Translator (wersja darmowa)",
                             "\nTranslated with www.DeepL.com/Translator (free version)\n",
                             "\nTranslated with www.DeepL.com/Translator (free version)"]

        with open(os.path.join(dir_path, filename), 'r', encoding='utf-8') as in_file:
            text: str = in_file.read()

        for freze in frezes:
            text = text.replace(freze, "")

        with open(os.path.join(dir_path, filename), 'w', encoding='utf-8') as out_file:
            out_file.write(text)

    @staticmethod
    def translate_google_gpt(filename: str, dir_path: str, translated_line_count: int, chat_gpt_access_token: str):
        translated_subs: pysrt.SubRipFile = SubtitleTranslator.translate_google(
            filename, dir_path, translated_line_count, is_combined_with_gpt=True)
        SubtitleTranslator.translate_chat_gpt(
            filename, dir_path, translated_line_count, chat_gpt_access_token, translated_subs)
        os.remove(os.path.join(dir_path, filename.replace(
            '.srt', '_translated_temp.srt')))

    @staticmethod
    def translate_chat_gpt(filename: str, dir_path: str, translated_line_count: int, chat_gpt_access_token: str, translated_subs: Optional[pysrt.SubRipFile] = None):
        chatbot = Chatbot(config={"access_token": chat_gpt_access_token})

        subs: pysrt.SubRipFile = pysrt.open(
            os.path.join(dir_path, filename), encoding='utf-8')
        groups: List[List[pysrt.SubRipItem]] = [subs[i:i+translated_line_count]
                                                for i in range(0, len(subs), translated_line_count)]

        additional_info: str = ""
        while True:
            info: str = input(
                "Dodaj dodatkowe informacje o tłumaczonym tekście (opcjonalnie): ")
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

            prompt: str = """NAJWAŻNIEJSZE: JEŚLI DOSTANIESZ NAPISY NP. 1 DO 30 TO ZWRÓĆ NAPISY 1 DO 30 NAWET JEŚLI TŁUMACZENIE DANEGO NAPISU JEST GŁUPIE, NIESPÓJNE, I OGÓLNIE ZŁĘ, BŁĄDNY NAPIS JEST LEPSZY NIŻ JEGO BRAK
Jesteś moim tłumaczem, specjalizującym się w przekładzie na język polski. Twoja rola nie ogranicza się do prostego tłumaczenia - jesteś również redaktorem i ulepszaczem języka. Komunikuję się z Tobą w różnych językach, a Twoim zadaniem jest identyfikowanie języka, tłumaczenie go i odpowiadanie poprawioną i ulepszoną wersją mojego tekstu, w języku polskim.

Zanim przystąpisz do tłumaczenia, poświęć chwilę na zrozumienie gramatycznych, językowych i kontekstualnych niuansów tekstu. Uchwyc subtelności i upewnij się, że tekst płynie jak strumień słów, jakby ktoś nam opowiadał historię, czytał audiobooka, czy narrację filmu, bo ostatecznie ten tekst będzie czytany na głos.

Twoim zadaniem jest podniesienie poziomu mojego języka, zastępując uproszczone słowa i zdania na poziomie C0 bardziej wyszukanymi i eleganckimi wyrażeniami. Zachowaj oryginalne znaczenie, ale uczyn język bardziej literackim. Twoje odpowiedzi powinny ograniczać się do poprawionego i ulepszonego tłumaczenia, bez dodatkowych wyjaśnień.

Podczas tłumaczenia, zachowaj dyskrecję w decydowaniu, kiedy tłumaczyć słowa dosłownie, a kiedy zachować zapożyczenia w ich oryginalnej formie. Unikaj używania polskich odpowiedników, które zniekształcają znaczenie lub estetykę zdania.

Zachowaj oryginalne formatowanie tekstu - nie dodawaj żadnych dodatkowych spacji, tabulatorów ani znaków nowej linii. Tekst, który tłumaczysz, może również przedstawiać akcje z książki, więc miej to na uwadze.

Podejdź globalnie do tekstu. Jeśli gdziekolwiek w tekście podano informacje o płci postaci, użyj tych informacji, aby kierować swoim tłumaczeniem przez cały tekst. Na przykład, zamiast tłumaczyć "I did it" jako "Zrobiłem to" lub "Zrobiłam to", przetłumacz to jako "To zostało zrobione przeze mnie", jeśli płeć nie jest określona. To podejście zmniejsza błędy tłumaczenia. Globalne podejście, nie tłumacz iteracyjnie słowo po słowie,  na przykład : "Święty Tyrs przegrał. Ona umarła.",  gdzie poprawnie to: "Święta Tyrs przegrała. Ona umarła."

Bądź kreatywny w swoich tłumaczeniach, dostosowując swój ton do kontekstu - bądź dowcipny dla lekkich tekstów i dodaj powagi i profesjonalizmu dla poważnych. Tłumacz wszystkie przekleństwa, nie cenzuruj i nie zmieniaj znaczenia słów, które są ważne w kontekście lub które zmieniają emocjonalny ton tekstu.

W tekście symbol '◍◍◍◍' reprezentuje nową linię w tym samym napisie, a symbol '@@' reprezentuje koniec napisu. Jeśli postanowisz pominąć jakiś napis, z jakichś powodów pamiętaj o zostawieniu znaku '@@', jest to kluczowe dla dalszego działania programu tłumaczeniowego. Nie zmieniaj ilości znaków '@@'.

Twoim ostatecznym celem jest wyprodukowanie tłumaczenia, które jest jak najbardziej wiernie odwzorowane na oryginał, zarówno pod względem znaczenia, jak i poprawności gramatycznej i syntaktycznej, chyba że oryginał jest niegramatyczny.

Zadanie wykonuj powoli krok po kroku

Dodatkowe informacje na temat tekstu który ma być tłumaczony: """ + additional_info + "\n\nTeraz przetłumacz poniższe napisy:\n" + text

            if translated_subs is not None:
                translated_text: str = "".join(
                    "◍◍{}. {}".format(
                        i + 1, translated_subs[i].text.replace('\n', ' ◍◍◍◍ ')
                    )
                    + " @@\n"
                    for i in range((counter - 1) - len(group), counter - 1)
                )
                translated_text = translated_text.rstrip(' @@\n')
                prompt += "\n\nNapisy wstępnie przetłumaczone przez Google Translate:\n" + translated_text

            prev_text: str = ""
            while True:
                for data in chatbot.ask(prompt):
                    prev_text = data["message"]

                translated_text: str = prev_text.rstrip(" @@\n")
                if translated_text:
                    translated_lines: List[str] = translated_text.split(" @@\n")
                    if len(translated_lines) != len(group):
                        print(
                            f"Błąd: liczba napisów po tłumaczeniu ({len(translated_lines)}) nie jest taka sama jak przed tłumaczeniem ({len(group)})")
                        prompt += "\n\nW poprzednim tłumaczeniu pominąłeś lub dodałeś dodatkowe napisy. Proszę przetłumacz ponownie poniższe napisy, tak aby liczba napisów była taka sama jak przed tłumaczeniem:\n" + text
                    else:
                        for sub, trans_text in zip(group, translated_lines):
                            trans_text = re.sub(r"◍◍\d+\. ", "", trans_text)
                            trans_text = trans_text.replace(" ◍◍◍◍, ", ",\n")
                            trans_text = trans_text.replace(" ◍◍◍◍ ", "\n")
                            trans_text = trans_text.replace(" ◍◍◍◍", "")
                            sub.text = trans_text
                        break

        subs.save(os.path.join(dir_path, filename), encoding='utf-8')

    def translate_srt(self,  filename: str, dir_path: str, settings: Settings):
        translator: str = settings.translator
        translated_line_count: int = int(settings.translated_line_count)
        deepl_api_key: str = settings.deepl_api_key

        self.console.print(f"Tłumaczenie napisów za pomocą {translator}...",
                           style='bold green')
        self.console.print(os.path.join(dir_path, filename))

        translator_functions = {
            'Google Translate': lambda *args:
                SubtitleTranslator.translate_google(*args[:3]),
            'DeepL API': lambda *args:
                SubtitleTranslator.translate_deepl_api(
                    *args[:3], deepl_api_key),
            'DeepL Desktop Free': lambda *args:
                SubtitleTranslator.translate_deepl_desktop(*args[:3]),
            'ChatGPT': lambda *args:
                SubtitleTranslator.translate_chat_gpt(
                    *args[:3], settings.chat_gpt_access_token),
            'ChatGPT + Google Translate': lambda *args:
                SubtitleTranslator.translate_google_gpt(
                    *args[:3], settings.chat_gpt_access_token)
        }

        if translator in translator_functions:
            translator_functions[translator](
                filename, dir_path, translated_line_count)
        else:
            self.console.print(
                f"Nieznany translator: {translator}", style='bold red')
