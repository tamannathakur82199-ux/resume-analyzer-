"""TF-IDF + cosine similarity in plain Python (no numpy / scikit-learn needed).

Same method as scikit-learn's TfidfVectorizer(stop_words='english', ngram_range=(1, 2),
sublinear_tf=True): smoothed idf, l2-normalised vectors, cosine similarity.
"""
from __future__ import annotations

import math
import re
from collections import Counter

STOP_WORDS = frozenset("""
a about above after again against all also am an and any are as at be because been before being below
between both but by can cannot could did do does doing down during each either else etc few for from
further had has have having he her here hers herself him himself his how i if in into is it its itself
just me more most my myself no nor not now of off on once only or other our ours ourselves out over own
same she should so some such than that the their theirs them themselves then there these they this those
through to too under until up upon us very was we were what when where which while who whom why will with
within without would you your yours yourself yourselves among around become becomes been beyond done
due eg every except get gets give go goes however ie many may might much must neither never next one
often per perhaps rather several since still therefore thus toward towards via whether whose yet
""".split())

_TOKEN = re.compile(r"(?u)\b\w\w+\b")


def _terms(text: str):
    words = [w for w in _TOKEN.findall(text.lower()) if w not in STOP_WORDS]
    terms = list(words)
    terms += [a + " " + b for a, b in zip(words, words[1:])]
    return terms


def tfidf_cosine(doc_a: str, doc_b: str) -> float:
    """Cosine similarity (0..1) of the TF-IDF vectors of two documents."""
    tf_a, tf_b = Counter(_terms(doc_a)), Counter(_terms(doc_b))
    if not tf_a or not tf_b:
        return 0.0
    n_docs = 2
    vocab = set(tf_a) | set(tf_b)
    idf = {t: math.log((1 + n_docs) / (1 + (t in tf_a) + (t in tf_b))) + 1 for t in vocab}

    def vector(tf):
        vec = {t: (1 + math.log(c)) * idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    va, vb = vector(tf_a), vector(tf_b)
    if len(va) > len(vb):
        va, vb = vb, va
    return float(sum(v * vb.get(t, 0.0) for t, v in va.items()))
