from typing import FrozenSet
from nltk import word_tokenize
from nltk.stem.snowball import EnglishStemmer


def tokenize(text: str) -> FrozenSet[str]:
    return frozenset(EnglishStemmer().stem(i) for i in word_tokenize(text) if i.isalnum())
