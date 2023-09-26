# https://chat.openai.com/api/auth/session

# {"user":{"id":"user-iyTwG8edDJc6nzquextcUxLg","name":"Mateusz Mróz","email":"mateuszmroz001@gmail.com","image":"https://lh3.googleusercontent.com/a/AGNmyxZ51xU7m0YcenfA1aPz0EcL0hntw4QZ_R522pPYEg=s96-c","picture":"https://lh3.googleusercontent.com/a/AGNmyxZ51xU7m0YcenfA1aPz0EcL0hntw4QZ_R522pPYEg=s96-c","idp":"google-oauth2","iat":1685039590,"mfa":false,"groups":["labs"],"intercom_hash":"df01ded94e393afa0d34abafe8a05dcecc2f8ef89b5eab1ecdd913340d19104e"},"expires":"2023-06-29T10:37:22.104Z","accessToken":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJtYXRldXN6bXJvejAwMUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sImh0dHBzOi8vYXBpLm9wZW5haS5jb20vYXV0aCI6eyJ1c2VyX2lkIjoidXNlci1peVR3RzhlZERKYzZuenF1ZXh0Y1V4TGcifSwiaXNzIjoiaHR0cHM6Ly9hdXRoMC5vcGVuYWkuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA3MjIwMDI0Mjc5OTM2OTA5MzUyIiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY4NTAzOTU5MCwiZXhwIjoxNjg2MjQ5MTkwLCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9yZ2FuaXphdGlvbi53cml0ZSJ9.e4Pwy2txj4NC5DR1mUQIz5EJNozPHwrxVxeH_e2w9LAN-u_70Nl09Bab9dVR8XkQLqGyH5-NUHuGbVhJYLBMpfgucuULEbBT-qNnvnftiWmIRiU5_W576bSDaOvFWAe8tKz4kwbxnHf_2MHV9xZc6HLysZYQ94AjlK4Cv8SEDVBH15Vl3wGmY4S_bUIEhSFoGzhVl_lfCqzUnsXa40CByZYXOgDnopC73nDa4c7JaR892ovH_CE7S1nUra8TYRoCg7CYLqlepGU4w5QxHs3s_gyb56xLytD3Eym5BS-v0oIpo5WbojmerwUGGRsPI8Hlt_vWYWkYfZ-Ztt6RI_rKVg","authProvider":"auth0"}

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
