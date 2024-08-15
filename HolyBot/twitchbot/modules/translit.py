from string import ascii_lowercase as ENGLISH_ALPHABET
import re

with open("english_words.txt", "r") as file:
    english_words = set(map(str.lower, re.sub("[^\w]", " ", file.read()).split()))

with open("russian_words.txt", "r") as file:
    russian_words = set(map(str.lower, re.sub("[^\w]", " ", file.read()).split()))

RUSSIAN_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
rus = "QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?qwertyuiop[]asdfghjkl;'\\zxcvbnm,./`~@#$%^&"
eng = "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,йцукенгшщзхъфывапролджэ\\ячсмитьбю.ёЁ\"№;%:?"
rus_to_eng = str.maketrans(rus, eng)
eng_to_rus = str.maketrans(eng, rus)

def fix_language(sentance: str):
    new_sentance = ""
    for word in sentance.split():
        if word.startswith("@"):
            new_sentance += word + " "
            continue
        elif is_english_word(word):
            translation_table = rus_to_eng
        elif is_russian_word(word):
            translation_table = eng_to_rus
        else:
            return None
        new_sentance += word.translate(translation_table) + " "
    if not is_english_sentance(new_sentance) and not is_russian_sentance(new_sentance):
        return None
    return new_sentance.strip()

def is_english_word(word: str):
    return (
        sum(letter.lower() in ENGLISH_ALPHABET for letter in word)
        / len(word)
    ) >= 0.5

def is_russian_word(word: str):
    return (
        sum(letter.lower() in RUSSIAN_ALPHABET for letter in word)
        / len(word)
    ) >= 0.5

def is_english_sentance(sentance: str):
    return (
        sum(word.lower() in english_words for word in sentance.split())
        / len(sentance.split())
    ) >= 0.5


def is_russian_sentance(sentance: str):
    return (
        sum(word.lower() in russian_words for word in sentance.split())
        / len(sentance.split())
    ) >= 0.5


def fix_if_needed(sentance: str):
    if not sentance:
        return None
    new_sentance = None
    if not is_english_sentance(sentance) and not is_russian_sentance(sentance):
        new_sentance = fix_language(sentance)
    return new_sentance

"""while True:
    a = input(">>> ")
    print(fix_if_needed(a))
"""
class Translit:
    def __init__(self) -> None:
        pass

    