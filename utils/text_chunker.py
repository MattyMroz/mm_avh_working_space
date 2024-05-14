import re


class LatinPunctuator:
    def getParagraphs(self, text):
        return self._recombine(re.split('((?:\r?\n\s*){2,})', text))

    def getSentences(self, text):
        # Dodano dodatkowe znaki interpunkcyjne do wyrażenia regularnego
        return self._recombine(re.split('([.!?]+[\s\u200b]+|…\s+)', text), r'\b(\w|[A-Z][a-z]|Assn|Ave|Capt|Col|Comdr|Corp|Cpl|Gen|Gov|Hon|Inc|Lieut|Ltd|Rev|Mr|Ms|Mrs|Dr|No|Univ|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec|dept|ed|est|vol|vs)\.\s+$')

    def getPhrases(self, sentence):
        # Dodano dodatkowe znaki interpunkcyjne do wyrażenia regularnego
        return self._recombine(re.split('([,;:]\s+|\s-+\s+|—\s*|『|』|「|」|„|”|«|»|〈|〉|\[|\]|\(|\)|\{|\}|"|\.\.\.\s+|\*\s+|\'\s+)', sentence))

    def getWords(self, sentence):
        # Dodano dodatkowe znaki interpunkcyjne do wyrażenia regularnego
        tokens = re.split(
            '([~@#%^*_+=<>|\[\](){}"『』「」„”«»〈〉\.\.\.\*\'\']|[\s\-—/]+|\.(?=\w{2,})|,(?=[0-9]))', sentence.strip())
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i]:
                result.append(tokens[i])
            if i+1 < len(tokens):
                if re.match(r'^[~@#%^*_+=<>|\[\](){}"『』「」„”«»〈〉...*\'\s]+$', tokens[i+1]):
                    result.append(tokens[i+1])
                elif result:
                    result[-1] += tokens[i+1]
            i += 2
        return result

    def _recombine(self, tokens, nonPunc=None):
        result = []
        for i in range(0, len(tokens), 2):
            part = tokens[i] + tokens[i+1] if i+1 < len(tokens) else tokens[i]
            if part:
                if nonPunc and result and result[-1] in nonPunc:
                    result[-1] += part
                else:
                    result.append(part)
        return result


class WordBreaker:
    def __init__(self, wordLimit, punctuator):
        self.wordLimit = wordLimit
        self.punctuator = punctuator

    def breakText(self, text):
        return [phrase for sentence in self.punctuator.getSentences(text) for phrase in self.breakSentence(sentence)]

    def breakParagraph(self, text):
        return list(self.punctuator.getPhrases(text))

    def breakSentence(self, sentence):
        return self.merge(self.punctuator.getPhrases(sentence), self.breakPhrase)

    def breakPhrase(self, phrase):
        words = self.punctuator.getWords(phrase)
        splitPoint = min(len(words) // 2, self.wordLimit)
        result = []
        while words:
            result.append(''.join(words[:splitPoint]))
            words = words[splitPoint:]
        return result

    def merge(self, parts, breakPart):
        result = []
        group = {'parts': [], 'wordCount': 0}

        def flush():
            nonlocal group
            if group['parts']:
                result.append(''.join(group['parts']))
                group = {'parts': [], 'wordCount': 0}

        for part in parts:
            wordCount = len(self.punctuator.getWords(part))
            if wordCount > self.wordLimit:
                flush()
                subParts = breakPart(part)
                result.extend(subParts)
            else:
                if group['wordCount'] + wordCount > self.wordLimit:
                    flush()
                group['parts'].append(part)
                group['wordCount'] += wordCount
        flush()
        return result


class CharBreaker:
    def __init__(self, charLimit, punctuator, paragraphCombineThreshold=None):
        self.charLimit = charLimit
        self.punctuator = punctuator
        self.paragraphCombineThreshold = paragraphCombineThreshold

    def breakText(self, text):
        return self.merge(self.punctuator.getParagraphs(text), self.breakParagraph, self.paragraphCombineThreshold)

    def breakParagraph(self, text):
        return self.merge(self.punctuator.getSentences(text), self.breakSentence)

    def breakSentence(self, sentence):
        return self.merge(self.punctuator.getPhrases(sentence), self.breakPhrase)

    def breakPhrase(self, phrase):
        return self.merge(self.punctuator.getWords(phrase), self.breakWord)

    def breakWord(self, word):
        result = []
        while word:
            result.append(word[:self.charLimit])
            word = word[self.charLimit:]
        return result

    def merge(self, parts, breakPart, combineThreshold=None):
        result = []
        group = {'parts': [], 'charCount': 0}

        def flush():
            if group['parts']:
                result.append(''.join(group['parts']))
                group['parts'] = []
                group['charCount'] = 0

        for part in parts:
            charCount = len(part)
            if charCount > self.charLimit:
                flush()
                subParts = breakPart(part)
                for subPart in subParts:
                    result.append(subPart)
            else:
                if (group['charCount'] + charCount) > (combineThreshold or self.charLimit):
                    flush()
                group['parts'].append(part)
                group['charCount'] += charCount
        flush()
        return result


def chunk_text(text, method='char', limit=750):
    punctuator = LatinPunctuator()
    if method == 'char':
        return CharBreaker(limit, punctuator).breakText(text)
    elif method == 'word':
        return WordBreaker(limit, punctuator).breakText(text)


def main():
    text = """
THE BEGINNING AFTER THE END, czyli POCZĄTEK PO KOŃCU.
Volume 1. Early Years.
King Grey has unrivaled strength, wealth, and prestige in a world governed by martial ability. However, solitude lingers closely behind those with great power. Beneath the glamorous exterior of a powerful king lurks the shell of a man, devoid of purpose and will.
    “While the power to control mana is largely genetic, there are many cases where children of Magi come out unable to sense the mana around them. A recent census showed that roughly one in every one hundred children are able to sense mana, but the extent of which could only be tested when their mana core first completely developed—anywhere from their early adolescence to late teen years. It will be apparent when a mage first awakens by the initial repellence of the surrounding mana when their mana core manifests. This results in a translucent barrier forming around the awakened that lasts a couple of minutes.”

Flipping through the pages, I found something that caught my attention.

“…Mana can be used in a couple of ways. The two most common methods of utilizing mana are: enhancement of the body with mana (augmenter), and emission of mana to the outside world (conjurer)…”

“…augmenters are most commonly seen amongst warriors who utilize mana, channeling it through their body to strengthen themselves and their attacks.”

“…The practice of conjuring is seen in Mages, who, after utilizing their mana, can cast spells to give off a certain effect on the surrounding area or directly at a target.”
"""
    test_1 = chunk_text(text, 'char', 100)
    for i, t in enumerate(test_1):
        print(f"Chunk {i+1}: {t}")
    print()
    test_2 = chunk_text(text, 'word', 100)
    for i, t in enumerate(test_2):
        print(f"Chunk {i+1}: {t}")


if __name__ == '__main__':
    main()
