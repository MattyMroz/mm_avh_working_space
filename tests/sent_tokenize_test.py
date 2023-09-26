from nltk.tokenize import sent_tokenize

text = "Good muffins cost $3.88 in New York. Please buy me two of them. Thanks. 1_2//21.23343 .12312. 12 312.213123"

sentences = sent_tokenize(text)
for i, sentence in enumerate(sentences, start=1):
    print(f"{i}\n00:00:00,000 --> 00:00:00,000\n{sentence}\n")
import nltk
nltk.download('punkt')

text = "Oto przykładowe zdanie w języku polskim."
tokens = nltk.word_tokenize(text)
print(tokens)
