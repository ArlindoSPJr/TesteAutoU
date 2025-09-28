import re
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer, SnowballStemmer

# Aponta para a pasta local onde você colocou os dados do nltk
nltk.data.path.append("src/nlp/data")

# Carrega stopwords sem tentar baixar
try:
    _PORTUGUESE_STOPWORDS = set(stopwords.words("portuguese"))
except LookupError:
    _PORTUGUESE_STOPWORDS = set()  # fallback vazio, evita quebrar o deploy

# Tenta usar RSLP (mais preciso para PT-BR), senão cai no Snowball
try:
    _stemmer = RSLPStemmer()
except Exception:
    _stemmer = SnowballStemmer("portuguese")

def normalize_whitespace(text: str) -> str:
    """Remove espaços extras e normaliza o texto"""
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text: str) -> List[str]:
    """Quebra texto em tokens alfanuméricos"""
    return re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)

def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove stopwords e tokens de 1 letra"""
    return [t for t in tokens if t not in _PORTUGUESE_STOPWORDS and len(t) > 1]

def stem_tokens(tokens: List[str]) -> List[str]:
    """Aplica stemming nos tokens"""
    return [_stemmer.stem(t) for t in tokens]

def preprocess(text: str, do_stem: bool = False) -> str:
    """Pré-processa texto (limpa, tokeniza, remove stopwords, e aplica stemming opcional)"""
    text = normalize_whitespace(text).lower()
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    if do_stem:
        tokens = stem_tokens(tokens)
    return " ".join(tokens)
