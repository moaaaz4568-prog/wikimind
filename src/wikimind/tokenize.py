"""Arabic/English tokenization for wikimind — standard library only.

Design (from the project research, phase 2):
- Arabic diacritics + tatweel are stripped; alef variants collapse to ا;
  teh marbuta ة -> ه, alef maksura ى -> ي, ؤ -> و, ئ -> ي.
- Latin text is lowercased; tokens are letter/digit runs.
- A small Arabic/English stopword list is dropped. No stemming is applied
  in v0.1 (stemming for Arabic is UNKNOWN/NOT_RUN — see docs/DESIGN.md).
"""

import re

DIACRITICS_RE = re.compile(r"[\u064b-\u0652\u0670\u0640]")
ALEF_RE = re.compile(r"[أإآٱ]")
NORMALIZE_MAP = str.maketrans({"ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"})
TOKEN_RE = re.compile(r"[^\W\d_]+|\d+", re.UNICODE)

STOPWORDS = frozenset("""
من في على إلى أن إن أو ثم ثمّ ما لا لم لن قد كل هذا هذه ذلك تلك هو هي هم هن كان كانت يكون تكون
عن مع بعد قبل بين عند لدى غير دون حتى كما لكن لكنّ إنّ أنّ ثمّ إذا لو أما أم هل أي كيف متى أين
الذي التي الذين اللاتي اللذين أولئك سؤال أسئلة شيء أشياء علاقة يوجد هناك ماذا لماذا حين عندما
بينما رغم رغم أن أيضا أيضا وأيضا فقط خاصة خصوصا نحو حول داخل خارج تحت فوق أمام خلف وراء
the a an and or of to in on for with as at by from is are was were be been it its this that
these those he she they we you i his her their our your my not no do does did have has had
will would can could should what which who when where why how is there here
""".split())


def normalize(text: str) -> str:
    """Normalize Arabic orthography + lowercase Latin."""
    text = DIACRITICS_RE.sub("", text)
    text = ALEF_RE.sub("ا", text)
    text = text.translate(NORMALIZE_MAP)
    return text.lower()


def tokenize(text: str) -> list:
    """Return content tokens: normalized, stopwords removed, len >= 2
    (single digits are kept)."""
    toks = []
    for tok in TOKEN_RE.findall(normalize(text)):
        if tok in STOPWORDS:
            continue
        if len(tok) < 2 and not tok.isdigit():
            continue
        toks.append(tok)
    return toks
