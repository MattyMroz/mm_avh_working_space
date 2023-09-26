# Tekst to speech po posluchu za pomocą lektora Ivona

# pip install pyttsx3
# pip install pysrt

# Sprawdzenie nazw dostępnych lektorów
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(voice.name)


print('\nMówi Zosia Harpo 22kHz:')
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Ustawienie prędkości mówienia
engine.setProperty('volume', 1)  # Ustawienie głośności
voices = engine.getProperty('voices')
for voice in voices:
    if voice.name == 'Vocalizer Expressive Zosia Harpo 22kHz':
        engine.setProperty('voice', voice.id)
        break

engine.say('Witaj świecie!')
engine.runAndWait()
