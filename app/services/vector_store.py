from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from loguru import logger
from app.utils.config import VECTOR_INDEX_PATH


@dataclass
class VectorHit:
    text: str
    score: float


class VectorStore:
    def __init__(self, index_dir: str | None = None) -> None:
        if not FAISS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning(
                "Vector store dependencies not available. "
                "Install faiss-cpu and sentence-transformers for full functionality. "
                "RAG queries will return empty results."
            )
            self.model = None
            self.index = None
            self.texts: List[str] = []
            self.dimension = 384  # Default dimension for all-MiniLM-L6-v2
            self.index_dir = index_dir or VECTOR_INDEX_PATH
            return
        
        self.index_dir = index_dir or VECTOR_INDEX_PATH
        os.makedirs(self.index_dir, exist_ok=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index_path = os.path.join(self.index_dir, "index.faiss")
        self.texts_path = os.path.join(self.index_dir, "texts.tsv")
        self.dimension = self.model.get_sentence_embedding_dimension()
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            self._load_texts()
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.texts: List[str] = []

    def _persist(self) -> None:
        if not FAISS_AVAILABLE or self.index is None:
            return
        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.texts_path, "w", encoding="utf-8") as f:
            for t in self.texts:
                f.write(t.replace("\n", " ") + "\n")

    def _load_texts(self) -> None:
        self.texts = []
        if os.path.exists(self.texts_path):
            with open(self.texts_path, "r", encoding="utf-8") as f:
                self.texts = [line.rstrip("\n") for line in f]
        else:
            self.texts = []

    def add_texts(self, texts: List[str]) -> None:
        if not texts:
            return
        if not FAISS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE or self.model is None or self.index is None:
            logger.warning("Vector store not available. Text not indexed.")
            return
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        self.index.add(embeddings)
        if not hasattr(self, "texts"):
            self.texts = []
        self.texts.extend(texts)
        self._persist()

    def query(self, question: str, k: int = 5) -> List[VectorHit]:
        if not FAISS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE or self.model is None or self.index is None:
            logger.warning("Vector store not available. RAG query returning empty results.")
            return []
        if not getattr(self, "texts", []):
            return []
        q = self.model.encode([question], normalize_embeddings=True)
        scores, idxs = self.index.search(q, k)
        hits: List[VectorHit] = []
        for i, score in zip(idxs[0], scores[0]):
            if i < 0 or i >= len(self.texts):
                continue
            hits.append(VectorHit(text=self.texts[i], score=float(score)))
        return hits
