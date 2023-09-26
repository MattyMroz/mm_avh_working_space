# Test 1 edge-tts in cmd:
from gtts import gTTS
import os



# Test 2 gtts in cmd:
mytext = "Witaj świecie! Mam na imię GOOGLE ASSISTANT."
audio = gTTS(text=mytext, lang="pl", slow=False)
audio.save("example.mp3")
os.system("start example.mp3")
