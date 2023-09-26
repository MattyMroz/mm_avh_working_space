"""
    Module `NumberInWords` provides a class `NumberInWords`
        that converts numbers into Polish words.
    It offers several functions that can be used in various contexts.

    -*- coding: utf-8 -*-

    * Example: First, create an instance of the `NumberInWords` class:
        number_in_words = NumberInWords()

    * Example usage of function `_number_in_words_3digits`:
        print(number_in_words._number_in_words_3digits(123))
            Outputs: "sto dwadzieścia trzy"

    * Example usage of function `_case`:
        print(number_in_words._case(1))     # Outputs: 0
        print(number_in_words._case(12))    # Outputs: 2
        print(number_in_words._case(23))    # Outputs: 1

    * Example usage of function `number_in_words`:
    Inputs: int, float, str (string works with long (30 digits, 15 on both sides) floating point numbers)
        print('Int: 123456789012345 =', number_in_words.number_in_words(123_456_789_012_345))
        print('Float: 0.123456789012345 =',
            number_in_words.number_in_words(0.123_456_789_012_345))
        print('String: 123456789012345.123456789012345 =',
            number_in_words.number_in_words('123_456_789_012_345.123_456_789_012_345'))
        print('String: 123456789012345,123456789012345 =',
            number_in_words.number_in_words('123_456_789_012_345,123_456_789_012_345'))

    * Example usage of function `thing_in_words`:
        print(number_in_words.thing_in_words(5, ["jabłko", "jabłka", "jabłek"]))
            Outputs: "pięć jabłek"

        print(number_in_words.thing_in_words(21, ["jabłko", "jabłka", "jabłek"]))
            Outputs: "dwadzieścia jeden jabłek"

    * Example usage of function `amount_in_words`:
        print(number_in_words.amount_in_words(1234.56))
            Outputs: "jeden tysiąc dwieście trzydzieści cztery złote 56/100"

        print(number_in_words.amount_in_words(567.89, fmt=1))
            Outputs: "pięćset sześćdziesiąt siedem złotych osiemdziesiąt dziewięć groszy"

    * Example usage of function `convert_numbers_in_text`:
        print(number_in_words.convert_numbers_in_text('Rozdział 69.2_3 / 4 (test96).'))
            Outputs: "Rozdział sześćdziesiąt dziewięć przecinek dwa_trzy / cztery (test dziewięćdziesiąt sześć)."
"""

import re
from dataclasses import dataclass, field
from typing import List, Union

from six import u


@dataclass
class NumberInWords:
    """
        NumberInWords is a class that converts numbers into Polish words.
    """

    UNITS: list = field(default_factory=lambda: [
        u(""), u("jeden"), u("dwa"), u("trzy"),
        u("cztery"), u("pięć"), u("sześć"),
        u("siedem"), u("osiem"), u("dziewięć")
    ])
    TENS: list = field(default_factory=lambda: [
        u(""), u("dziesięć"), u("dwadzieścia"), u("trzydzieści"),
        u("czterdzieści"), u("pięćdziesiąt"), u("sześćdziesiąt"),
        u("siedemdziesiąt"), u(
            "osiemdziesiąt"), u("dziewięćdziesiąt")
    ])
    TEENS: list = field(default_factory=lambda: [
        u("dziesięć"), u("jedenaście"), u("dwanaście"),
        u("trzynaście"), u("czternaście"), u("piętnaście"),
        u("szesnaście"), u("siedemnaście"), u("osiemnaście"),
        u("dziewiętnaście")
    ])
    HUNDREDS: list = field(default_factory=lambda: [
        u(""), u("sto"), u("dwieście"), u("trzysta"),
        u("czterysta"), u("pięćset"), u("sześćset"),
        u("siedemset"), u("osiemset"), u("dziewięćset")
    ])
    BIG: list = field(default_factory=lambda: [
        [u("x"), u("x"), u("x")],
        [u("tysiąc"), u("tysiące"), u("tysięcy")],
        [u("milion"), u("miliony"), u("milionów")],
        [u("miliard"), u("miliardy"), u("miliardów")],
        [u("bilion"), u("biliony"), u("bilionów")],
        # Add more if needed
    ])
    ZLOTYS: list = field(default_factory=lambda: [
                         u("złoty"), u("złote"), u("złotych")
                         ])
    GROSZES: list = field(default_factory=lambda: [
                          u("grosz"), u("grosze"), u("groszy")
                          ])

    def _number_in_words_3digits(self, number: int) -> str:
        """
            This method converts a three-digit number into words in Polish.
        """
        unit: int = number % 10
        ten: int = (number // 10) % 10
        hundred: int = (number // 100) % 10
        words: List[str] = []

        if hundred > 0:
            words.append(self.HUNDREDS[hundred])
        if ten == 1:
            words.append(self.TEENS[unit])
        else:
            if ten > 0:
                words.append(self.TENS[ten])
            if unit > 0:
                words.append(self.UNITS[unit])
        return u(" ").join(words)

    def _case(self, number: int) -> int:
        """
            This method determines the grammatical case for a given number. It's used to correctly form the word for thousands, millions, etc. in Polish.
        """
        if number == 1:
            return 0
        unit: int = number % 10
        return 2 if (number // 10) % 10 == 1 and unit > 1 or not 2 <= unit <= 4 else 1

    def number_in_words(self, number: Union[int, float, str]) -> str:
        """
            This method converts a number (including decimal numbers) into words in Polish.
        """
        if isinstance(number, (int, float)):
            number = str(number)

        if '.' in number:
            integer_part: int
            decimal_part: int
            integer_part, decimal_part = map(int, number.split('.'))
        elif ',' in number:
            integer_part: int
            decimal_part: int
            integer_part, decimal_part = map(int, number.split(','))
        else:
            integer_part: int = int(number)
            decimal_part: int = 0

        words: List[str] = []
        if integer_part == 0:
            words.append(u("zero"))
        else:
            triples: List[int] = []
            while integer_part > 0:
                triples.append(integer_part % 1000)
                integer_part //= 1000
            for i, n in enumerate(triples):
                if n > 0:
                    if i > 0 and n == 1:
                        p: int = self._case(n)
                        w: str = self.BIG[i][p]
                        words.append(w)
                    elif i > 0:
                        p: int = self._case(n)
                        w: str = self.BIG[i][p]
                        words.append(
                            self._number_in_words_3digits(n) + u(" ") + w)
                    else:
                        words.append(self._number_in_words_3digits(n))
            words.reverse()

        if decimal_part != 0:
            words.extend(
                (u("przecinek"), self.number_in_words(str(decimal_part))))
        return u(" ").join(words)

    def thing_in_words(self, number: int, thing: List[str]) -> str:
        """
            This method converts a number into words and appends the correct form of a noun. The noun's form depends on the number and is given as a list of three forms for different cases.

            In words "how many things"

            Args:
                - number - int
                - thing - array of cases [coś, cosie, cosiów]

        """
        return self.number_in_words(number) + u(" ") + thing[self._case(number)]

    def amount_in_words(self, number: float, fmt: int = 0) -> str:
        """
            This method converts a monetary amount into words in Polish. The amount is given as a float, where the integer part is the number of zlotys and the fractional part is the number of groszes. The fmt parameter determines how groszes are formatted: if fmt is 0, groszes are in the form xx/100, otherwise they are converted into words.

            In words zlotys, groszes.

            Args:
                - number - float, number of zlotys with groszes after the comma
                - fmt - (format) if 0, then groszes in the form xx/100, in words in p. case
        """
        lzlotys: int = int(number)
        lgroszes: int = int(number * 100 + 0.5) % 100
        if fmt != 0:
            grosz_in_words: str = self.thing_in_words(lgroszes, self.GROSZES)
        else:
            grosz_in_words: str = u("%d/100") % lgroszes
        return self.thing_in_words(lzlotys, self.ZLOTYS) + u(" ") + grosz_in_words

    def convert_numbers_in_text(self, text: str) -> str:
        """
            This method converts numbers in a text into words in Polish. Yes is not perfect, but it works in most cases. If you want grammatical correctness use AI.
        """
        result: str = ''
        number: str = ''
        special_chars: List[str] = ['!', '@', '#', '$', '%', '^', '&', '*',
                                    '(', ')', '_', '+', '~', '`', '{', '}', '|', '[', ']', '\\', ':', '"', ';', "'", '<', '>', '?', '/', '-']
        for i, char in enumerate(text):
            if char.isdigit() or (char in ['.', ','] and i > 0 and i < len(text) - 1 and text[i-1].isdigit() and text[i+1].isdigit()):
                number += char
            else:
                if number and number not in special_chars:
                    for special_char in special_chars:
                        if number.count(special_char) > 1:
                            for part in number.split(special_char):
                                number_in_words: str = self.number_in_words(
                                    part)
                                result += number_in_words + special_char
                            # Usuwamy ostatni znak specjalny
                            result = result[:-1]
                            break
                    else:
                        if number.count('.') == 1 or number.count(',') == 1:
                            number_in_words: str = self.number_in_words(number)
                            if (
                                result
                                and not result[-1].isspace()
                                and result[-1] not in special_chars
                            ):
                                result += ' '
                            result += number_in_words
                        else:
                            parts: List[str] = re.split('(\D)', number)
                            for part in parts:
                                if part.isdigit():
                                    number_in_words: str = self.number_in_words(
                                        part)
                                    if (
                                        result
                                        and not result[-1].isspace()
                                        and result[-1] not in special_chars
                                    ):
                                        result += ' '
                                    result += number_in_words
                                else:
                                    result += part
                    if (
                        i < len(text) - 1
                        and not text[i].isspace()
                        and text[i] not in special_chars
                    ):
                        result += ' '
                    number = ''
                result += char
        if number and number not in special_chars:
            number_in_words: str = self.number_in_words(number)
            if (
                result
                and not result[-1].isspace()
                and result[-1] not in special_chars
            ):
                result += ' '
            result += number_in_words
        return result
