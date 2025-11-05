from __future__ import annotations

from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_sentences(text: str) -> List[str]:
    # very simple splitter; replace with nltk/spacy if needed
    parts = [s.strip() for s in text.replace("\n", " ").split(".")]
    return [p for p in parts if p]


def summarize_text(chunks: List[str], max_sentences: int = 5) -> str:
    if not chunks:
        return ""
    sentences: List[str] = []
    for c in chunks:
        sentences.extend(split_sentences(c))
    if not sentences:
        return ""
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences)
    centroid = X.mean(axis=0)
    sims = cosine_similarity(X, centroid)
    ranked = sorted(range(len(sentences)), key=lambda i: sims[i, 0], reverse=True)
    top = sorted(ranked[: max_sentences], key=lambda i: i)
    return ". ".join(sentences[i] for i in top).strip() + "."
