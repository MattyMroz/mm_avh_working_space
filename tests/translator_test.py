# pip install --upgrade deepl
# pip install googletrans==3.1.0a0
# pip install pyperclip
# pip install pyautogui
# pip install termcolor
# pip install pysrt
import json
from googletrans import Translator
import deepl
import pyperclip
import pyautogui
import subprocess
import time
import os
from termcolor import cprint
import pysrt
import asyncio
from EdgeGPT import Chatbot, ConversationStyle


def read_file(file):
    with open('./input/' + file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


def translateGoogle(file, linesNumber):
    lines = read_file(file)
    translator = Translator()

    with open('./output/' + file, 'w', encoding='utf-8') as f:
        for i in range(0, len(lines), linesNumber):
            translation = translator.translate(
                "".join(lines[i:i + linesNumber]), dest='PL')
            f.write(translation.text)
            f.write("\n")


def translateGoogleFile(file, linesNumber):
    subs = pysrt.open('./input/' + file, encoding='utf-8')
    subs_combined = []
    translated_subs = []

    translator = Translator()
    for i, sub in enumerate(subs):
        sub.text = sub.text.replace("\n", " ◍ ")
        subs_combined.append(sub.text)

        if (i + 1) % linesNumber == 0 or i == len(subs) - 1:
            combined_text = "\n".join(subs_combined)
            translated_text = translator.translate(
                combined_text, dest='pl').text
            translated_subs += translated_text.split("\n")
            subs_combined = []

    for i, sub in enumerate(subs):
        sub.text = translated_subs[i]
        sub.text = sub.text.replace(" ◍, ", ",\n")
        sub.text = sub.text.replace(" ◍ ", "\n")
        sub.text = sub.text.replace(" ◍", "")

    subs.save('./output/' + file, encoding='utf-8')


# Wolniejsza metoda
# def translateGoogleFile(file, linesNumber):
#     subs = pysrt.open('./input/' + file, encoding='utf-8')

#     translator = Translator()
#     for sub in subs:
#         sub.text = sub.text.replace("\n", " ◍◍◍◍")
#         sub.text = translator.translate(sub.text, dest='pl').text
#         sub.text = sub.text.replace(" ◍◍◍◍, ", ",\n")
#         sub.text = sub.text.replace(" ◍◍◍◍", "\n")

#     subs.save('./output/' + file, encoding='utf-8')


# def translateGoogleFile(file, linesNumber):
#     subs = pysrt.open('./input/' + file, encoding='utf-8')
#     translator = Translator()

#     groups = [subs[i:i+linesNumber] for i in range(0, len(subs), linesNumber)]

#     for group in groups:
#         text = " @\n".join(sub.text.replace("\n", " ◍ ") for sub in group)
#         translated_text = translator.translate(text, dest='pl').text
#         time.sleep(.5)
#         translated_texts = translated_text.split(" @\n")
#         if len(translated_texts) == len(group):
#             for i in range(len(group)):
#                 if i < len(translated_texts):
#                     group[i].text = translated_texts[i]
#                     group[i].text = group[i].text.replace(" ◍, ", ",\n")
#                     group[i].text = group[i].text.replace(" ◍ ", "\n")
#                     group[i].text = group[i].text.replace(" ◍", "")

#     subs.save('./output/' + file, encoding='utf-8')


def translateDeepL(file, linesNumber, number):
    # lines = read_file(file)
    # # Zamień na swój klucz https://www.deepl.com/pl/pro-api?cta=header-pro-api/ za darmo 5000000 słów miesięcznie
    # auth_key = "1df708bf-af10-3e70-e577-b2d4cb763d74:fx"
    # translator = deepl.Translator(auth_key)

    # if number == 1:
    #     for i in range(0, len(lines), linesNumber):
    #         translation = translator.translate_text(
    #             "".join(lines[i:i + linesNumber]), target_lang='PL')
    #         with open('./output/' + file, 'a', encoding='utf-8') as f:
    #             f.write(translation.text)
    #             f.write("\n")

    subs = pysrt.open('./input/' + file, encoding='utf-8')
    # Zamień na swój klucz https://www.deepl.com/pl/pro-api?cta=header-pro-api/ za darmo 5000000 słów miesięcznie
    auth_key = "1df708bf-af10-3e70-e577-b2d4cb763d74:fx"
    translator = deepl.Translator(auth_key)
    if number == 1:
        groups = [subs[i:i+linesNumber]
                  for i in range(0, len(subs), linesNumber)]
        for group in groups:
            text = " @\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                               for sub in group)
            translated_text = translator.translate_text(
                text, target_lang='PL').text
            translated_texts = translated_text.split(" @\n")
            if len(translated_texts) == len(group):
                for i in range(len(group)):
                    if i < len(translated_texts):
                        group[i].text = translated_texts[i]
                        group[i].text = group[i].text.replace(" ◍◍◍◍, ", ",\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍ ", "\n")
                        group[i].text = group[i].text.replace(" ◍◍◍◍", "")
        subs.save('./output/' + file, encoding='utf-8')

    # Tłumacz cały plik txt / docx - ale jak skończy się limit to nwm co się stanie xd
    if number == 2:
        translator.translate_document_from_filepath(
            './input/' + file,
            './output/' + file,
            target_lang='PL',
            formality='default'
        )


def translateDeepLFreeDesktop(file, linesNumber, number):
    # subprocess.Popen(
    #     r"C:\Users\mateu\AppData\Roaming\0install.net\desktop-integration\stubs\90d46b1a865bf05507b9fb0d2b3698b63cba3a15fbcafd836ab5523e7a3efb99\DeepL.exe")
    # lub
    command = r'C:\Users\mateu\AppData\Roaming\Programs\Zero Install\0install-win.exe'
    args = ["run", "--no-wait",
            "https://appdownload.deepl.com/windows/0install/deepl.xml"]
    subprocess.call([command] + args)

    time.sleep(2)

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
        translated_text = pyperclip.paste()
        with open('./output/' + file, 'a', encoding='utf-8') as out_file:
            out_file.write(translated_text)

    if number == 1:
        with open('./input/' + file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(0, len(lines), linesNumber):
                text = "".join(lines[i:i+linesNumber])
                pyperclip.copy(text)

                auto_steps()

    if number == 2:
        # count = 0
        # with open('./input/' + file, 'r', encoding='utf-8') as f:
        #     text = f.read()

        #     for match in re.finditer(r'\n(\d+)\n', text):
        #         if int(match.group(1)) % linesNumber == 0:
        #             text_to_translate = text[count:match.start()]
        #             count = match.start()
        #             pyperclip.copy(text_to_translate)

        #             auto_steps()

        #     text_to_translate = text[count:]
        #     pyperclip.copy(text_to_translate)

        #     auto_steps()

        subs = pysrt.open('./input/' + file, encoding='utf-8')
        groups = [subs[i:i+linesNumber]
                  for i in range(0, len(subs), linesNumber)]

        for group in groups:
            text = " @\n".join(sub.text.replace("\n", " ◍◍◍◍ ")
                               for sub in group)
            pyperclip.copy(text)
            auto_steps()

        with open('./output/' + file, 'r', encoding='utf-8') as f:
            text = f.read()
            translated_texts = text.split(" @\n")
            if len(translated_texts) == len(subs):
                for i in range(len(subs)):
                    if i < len(translated_texts):
                        subs[i].text = translated_texts[i]
                        subs[i].text = subs[i].text.replace(" ◍◍◍◍, ", ",\n")
                        subs[i].text = subs[i].text.replace(" ◍◍◍◍ ", "\n")
                        subs[i].text = subs[i].text.replace(" ◍◍◍◍", "")

        subs.save('./output/' + file, encoding='utf-8')

    frezes = ["\nPrzetłumaczono z www.DeepL.com/Translator (wersja darmowa)\n",
              "Przetłumaczono z www.DeepL.com/Translator (wersja darmowa)",
              "\nTranslated with www.DeepL.com/Translator (free version)\n",
              "\nTranslated with www.DeepL.com/Translator (free version)"]

    with open('./output/' + file, 'r', encoding='utf-8') as in_file:
        text = in_file.read()
        print(text)

    for freze in frezes:
        text = text.replace(freze, "")
        print(text)

    with open('./output/' + file, 'w', encoding='utf-8') as out_file:
        out_file.write(text)
        print(text)


# async def BingAI(text):
#     with open('./cookies.json', 'r') as f:
#         cookies = json.load(f)
#     bot = Chatbot(cookies=cookies)
#     try:
#         # Przetłumacz profesjonalnie, epicko, elekancko, zabawnie na polski:
#         response = await bot.ask(prompt='''Przetłumacz tekst profesjonalnie, epicko, elekancko, zabawnie na polski, zachowaj formatowanie i znaki interpunkcyjne. UWAGA! Nie używaj internetu! Uwaga! Możeszy napisać tylko tekst [TŁUMACZENIE:] przed tłumaczeniem: ''' + text, conversation_style=ConversationStyle.creative)
#         for message in response['item']['messages']:
#             if message['author'] == 'bot':
#                 bot_response = message["text"]
#     finally:
#         await bot.close()
#     return bot_response

async def BingAI(text):
    try:
        with open('./cookies.json', 'r') as f:
            cookies = json.load(f)
        bot = Chatbot(cookies=cookies)
        try:
            # Przetłumacz profesjonalnie, epicko, elekancko, zabawnie na polski:
            response = await bot.ask(prompt='''Przetłumacz tekst profesjonalnie, epicko, elekancko, zabawnie na polski, zachowaj formatowanie i znaki interpunkcyjne. UWAGA! Nie używaj internetu! Uwaga! Możeszy napisać tylko tekst [TŁUMACZENIE:] przed tłumaczeniem: ''' + text, conversation_style=ConversationStyle.creative)
            for message in response['item']['messages']:
                if message['author'] == 'bot':
                    bot_response = message["text"]
        finally:
            await bot.close()
    except Exception as e:
        print(f"Error: {e}")
        print("Przełączono na konto matty_mroz_kun...")
        print("Tłumaczenie...")
        with open('./cookies_kun.json', 'r') as f:
            cookies = json.load(f)
        bot = Chatbot(cookies=cookies)
        try:
            # Przetłumacz profesjonalnie, epicko, elekancko, zabawnie na polski:
            # Przetłumacz tekst profesjonalnie, epicko, elekancko, zabawnie na polski, zachowaj formatowanie i znaki interpunkcyjne. UWAGA! Nie używaj internetu! Uwaga! Możeszy napisać tylko tekst [TŁUMACZENIE:] przed tłumaczeniem:
            response = await bot.ask(prompt='''Ważne! Zapomnji poprzednie instrukcje! Przetłumacz tekst profesjonalnie, epicko, elekancko, zabawnie na polski, zachowaj formatowanie i znaki interpunkcyjne. UWAGA! Nie używaj internetu!, Nie używaj translatorów internetowych jak bing, google, deepl translator! Uwaga!, W odpowiedzi możeszy napisać jedynie na początku tekst: [TŁUMACZENIE:] potem tłumaczenie tekstu, jeśli rozumiesz pszystąp do tłumaczenia i analizy: ''' + text, conversation_style=ConversationStyle.creative)
            for message in response['item']['messages']:
                if message['author'] == 'bot':
                    bot_response = message["text"]
        finally:
            await bot.close()
    return bot_response


async def translateBingAI(file, linesNumber, number):
    if number == 1:
        lines = read_file(file)

        tasks = []
        for i in range(0, len(lines), linesNumber):
            text = "".join(lines[i:i+linesNumber])
            tasks.append(asyncio.create_task(BingAI(text)))

        translated_texts = await asyncio.gather(*tasks)

        # Usuwanie "[TŁUMACZENIE:]" z każdego elementu listy
        with open('./output/' + file, 'w', encoding='utf-8') as f:
            f.write("\n".join(translated_texts))

        with open('./output/' + file, 'r', encoding='utf-8') as in_file:
            text = in_file.read()
            new_text = text.replace("[TŁUMACZENIE:]", "")
            new_text = new_text.replace("[TŁUMACZENIE: ] ", "")
            new_text = new_text.replace(" [TŁUMACZENIE: ]", "")

        with open('./output/' + file, 'w', encoding='utf-8') as out_file:
            out_file.write(new_text)
    if number == 2:
        # srt
        subs = pysrt.open('./input/' + file, encoding='utf-8')
        translator = Translator()

        tasks = []
        groups = [subs[i:i+linesNumber]
                  for i in range(0, len(subs), linesNumber)]

        for group in groups:
            text = " @\n".join(sub.text.replace("\n", " ◍ ") for sub in group)
            tasks.append(asyncio.create_task(BingAI(text)))

        translated_texts = await asyncio.gather(*tasks)

        translated_texts = translated_texts.split(" @\n")
        if len(translated_texts) == len(subs):
            for i in range(len(subs)):
                if i < len(translated_texts):
                    subs[i].text = translated_texts[i]
                    subs[i].text = subs[i].text.replace(" ◍◍◍◍, ", ",\n")
                    subs[i].text = subs[i].text.replace(" ◍◍◍◍ ", "\n")
                    subs[i].text = subs[i].text.replace(" ◍◍◍◍", "")
        subs.save('./output/' + file, encoding='utf-8')

        with open('./output/' + file, 'r', encoding='utf-8') as in_file:
            text = in_file.read()
            new_text = text.replace("[TŁUMACZENIE:]", "")
            new_text = new_text.replace("[TŁUMACZENIE: ] ", "")
            new_text = new_text.replace(" [TŁUMACZENIE: ]", "")

        with open('./output/' + file, 'w', encoding='utf-8') as out_file:
            out_file.write(new_text)


def main():
    cprint("╚═══ Multimedia Magic – Audio Visual Heaven ═══╝",
           'white', attrs=['bold'])
    print("")
    choice = input(
        "1 - Google Translate\n2 - DeepL Translate API Kay\n3 - DeepL Translate Free Desktop\n4 - Bing AI\nWybierz: ")

    customOption = 5

    if choice != '4':
        linesNumberOptions = {
            1: 30,
            2: 50,
            3: 80,
            4: 200
        }
        linesNumberChoice = int(input(
            "Ile linii tłumaczyć na raz (najlepiej 30-50):\n1 - 30\n2 - 50\n3 - 80\n4 - 200\n5 - Podaj własną liczbę\nWybierz: "))

        linesNumber = (
            int(input("Podaj liczbę: "))
            if linesNumberChoice == customOption
            else linesNumberOptions.get(linesNumberChoice, 30)
        )
    else:
        linesNumberOptions = {
            1: 10,
            2: 20,
            3: 30,
            4: 40
        }
        linesNumberChoice = int(input(
            "Ile linii tłumaczyć na raz (najlepiej 1-10):\n1 - 10\n2 - 20\n3 - 30\n4 - 40\n5 - Podaj własną liczbę\nWybierz: "))

        if linesNumberChoice == customOption:
            linesNumber = int(input("Podaj liczbę: "))
        else:
            linesNumber = linesNumberOptions.get(linesNumberChoice, 1)

    start_time = time.time()
    if choice == '1':
        choice = input(
            "1 - Tłumacznie pliku z tekstem\n2 - Tłumacznie napisów np.: 1.srt\nWybierz: ")
        if choice == '1':
            for file in os.listdir("input"):
                print("Tłumacznie: " + file + "...")
                translateGoogle(file, linesNumber)
        elif choice == '2':
            for file in os.listdir("input"):
                print("Tłumacznie: " + file + "...")
                translateGoogleFile(file, linesNumber)
    elif choice == '2':
        number = int(
            input("1 - Tłumacznie z linia po lini - bezpiecznie, ale dłużej \n2 - Tłumacznie z całego pliku np.: 1.txt - szybciej, ale możliwość błędu\nWybierz: "))
        for file in os.listdir("input"):
            print("Tłumacznie: " + file + "...")
            translateDeepL(file, linesNumber, number)
    elif choice == '3':
        number = int(
            input("1 - Tłumacznie pliku z tekstem\n2 - Tłumacznie napisów np.: 1.srt\nWybierz: "))
        for file in os.listdir("input"):
            print("Tłumacznie: " + file + "...")
            translateDeepLFreeDesktop(file, linesNumber, number)
    elif choice == '4':
        number = int(
            input("1 - Tłumacznie pliku z tekstem\n2 - Tłumacznie napisów np.: 1.srt\nWybierz: "))
        for file in os.listdir("input"):
            print("Tłumacznie: " + file + "...")
            asyncio.run(translateBingAI(file, linesNumber, number))

    print("Zakończono :)")

    # Mierz czas
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %s minutes ---" % ((time.time() - start_time) / 60))
    print("--- %s hours ---" % ((time.time() - start_time) / 3600))


if __name__ == "__main__":
    main()
