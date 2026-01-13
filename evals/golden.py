import re
import unicodedata
from typing import List, Tuple

def strip_accents(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s)
        if unicodedata.category(ch) != "Mn"
    )

def normalize(s: str) -> str:
    s = s.lower().strip()
    s = strip_accents(s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokens(s: str) -> List[str]:
    n = normalize(s)
    return [t for t in n.split(" ") if t]

def token_f1(actual: str, expected: str) -> Tuple[float, float, float]:
    a = tokens(actual)
    e = tokens(expected)
    if not a or not e:
        return 0.0, 0.0, 0.0

    e_remaining = e[:]
    inter = 0
    for t in a:
        if t in e_remaining:
            inter += 1
            e_remaining.remove(t)

    precision = inter / max(len(a), 1)
    recall = inter / max(len(e), 1)
    f1 = 0.0 if (precision + recall) == 0 else (2 * precision * recall / (precision + recall))
    return f1, precision, recall
