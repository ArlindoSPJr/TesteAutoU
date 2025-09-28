import re
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer, SnowballStemmer

# Ensure resources
try:
    _ = stopwords.words('portuguese')
except LookupError:
    nltk.download('stopwords')

_PORTUGUESE_STOPWORDS = set(stopwords.words('portuguese'))

try:
    _stemmer = RSLPStemmer()
except Exception:
    _stemmer = SnowballStemmer('portuguese')

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)

def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in _PORTUGUESE_STOPWORDS and len(t) > 1]

def stem_tokens(tokens: List[str]) -> List[str]:
    return [_stemmer.stem(t) for t in tokens]

def preprocess(text: str, do_stem: bool = False) -> str:
    text = normalize_whitespace(text)
    text = text.lower()
    tokens = tokenize(text)
    return " ".join(tokens)