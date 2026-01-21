import re
from typing import Iterable

REFUSAL_HINTS = [
    "nie mogę", "nie moge", "nie jestem w stanie", "nie posiadam", "nie mam dostępu",
    "as an ai", "i can't", "i cannot", "sorry", "nie wiem",
]

def normalize(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("\u00A0", " ")  # nbsp
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" \t\r\n.,;:!?\"'`()[]{}")
    return s

def contains_any(haystack: str, needles: Iterable[str]) -> bool:
    h = normalize(haystack)
    for n in needles:
        if normalize(n) in h:
            return True
    return False


def contains_word(haystack: str, words: Iterable[str]) -> bool:
    """Check if any word appears as whole word (using word boundaries)."""
    h = normalize(haystack)
    for w in words:
        pattern = r'\b' + re.escape(normalize(w)) + r'\b'
        if re.search(pattern, h):
            return True
    return False

def contains_any_raw(haystack: str, needles: Iterable[str]) -> bool:
    h = haystack.lower()
    for n in needles:
        if n.lower() in h:
            return True
    return False

def looks_like_refusal(text: str) -> bool:
    return contains_any_raw(text, REFUSAL_HINTS)

def only_number(text: str) -> bool:
    t = text.strip()
    return bool(re.fullmatch(r"\d+", t))
