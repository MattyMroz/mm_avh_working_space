# https://chat.openai.com/api/auth/session

# Przykładowa odpowiedź z /api/auth/session (token i dane użytkownika usunięte — wklej własne lokalnie):
# {"user":{...},"expires":"...","accessToken":"YOUR_ACCESS_TOKEN","authProvider":"auth0"}

# Napisz funckjie obsugująca chat najpierw poproś o  access_token wyświetlając strone w przegląderce kodem poniżej (zapisz w funckji)
# import webbrowser

# url = "https://chat.openai.com/api/auth/session"

# # Otwórz stronę w domyślnej przeglądarce
# webbrowser.open(url)


# # potem zainicjiuj chat uwaga ask_chatGPT powinna zwracać odpowiedz w while powinno ją wypisywać
# # pip install revChatGPT
# from revChatGPT.V1 import Chatbot
# chatbot = Chatbot(config={
#     "access_token": ""
# })


# def ask_chatGPT(prompt):
#     print("ChatGPT: ", end="")
#     prev_text = ""
#     for data in chatbot.ask(
#         prompt,
#     ):
#         message = data["message"][len(prev_text):]
#         print(message, end="", flush=True)
#         prev_text = data["message"]
#     print('\n')


# prompt = "Co tam?"
# # prompt = input("You: ")
# while prompt != "Exit":
#     ask_chatGPT(prompt)
#     prompt = input("You: ")
import webbrowser
from revChatGPT.V1 import Chatbot


def get_access_token():
    # Otwórz stronę w domyślnej przeglądarce
    url = "https://chat.openai.com/api/auth/session"
    webbrowser.open(url)

    return input("Podaj access_token: ")


# Inicjalizuj chat
chatbot = Chatbot(config={"access_token": get_access_token()})


def ask_chatGPT(prompt):
    print("ChatGPT: ", end="")
    prev_text = ""
    for data in chatbot.ask(
        prompt
    ):
        prev_text = data["message"]
    # print(prev_text)
    return prev_text


prompt = "Co tam?"
# prompt = input("You: ")
while prompt != "Exit":
    print(ask_chatGPT(prompt))
    prompt = input("You: ")
