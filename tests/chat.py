# https://chat.openai.com/api/auth/session

# {"user":{"id":"user-iyTwG8edDJc6nzquextcUxLg","name":"Mateusz Mróz","email":"REDACTED@example.com","image":"https://lh3.googleusercontent.com/a/AGNmyxZ51xU7m0YcenfA1aPz0EcL0hntw4QZ_R522pPYEg=s96-c","picture":"https://lh3.googleusercontent.com/a/AGNmyxZ51xU7m0YcenfA1aPz0EcL0hntw4QZ_R522pPYEg=s96-c","idp":"google-oauth2","iat":1685039590,"mfa":false,"groups":["labs"],"intercom_hash":"REDACTED"},"expires":"2023-06-29T10:37:22.104Z","accessToken":"YOUR_OPENAI_ACCESS_TOKEN","authProvider":"auth0"}

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
