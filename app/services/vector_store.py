import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.text_splitter import TextChunk


class LocalVectorStore:
    """A lightweight local vector store based on TF-IDF.

    This implementation is intentionally simple for local interview demos.
    The class boundary allows replacing it with FAISS, Chroma, Milvus, etc.
    """

    def __init__(self, persist_path: Path):
        self.persist_path = persist_path
        self.chunks: List[TextChunk] = []
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=20000)
        self.matrix = None
        self.load()

    def build(self, chunks: Iterable[TextChunk]) -> None:
        self.chunks = list(chunks)
        if not self.chunks:
            self.matrix = None
            self.save()
            return
        corpus = [chunk.content for chunk in self.chunks]
        self.matrix = self.vectorizer.fit_transform(corpus)
        self.save()

    def add_and_rebuild(self, chunks: Iterable[TextChunk]) -> None:
        self.chunks.extend(list(chunks))
        self.build(self.chunks)

    def search(self, query: str, top_k: int = 4) -> List[dict]:
        if not self.chunks or self.matrix is None:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        if scores.size == 0:
            return []
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0:
                continue
            chunk = self.chunks[int(idx)]
            results.append(
                {
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "score": round(score, 4),
                }
            )
        return results

    def save(self) -> None:
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(chunk) for chunk in self.chunks]
        self.persist_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.persist_path.exists():
            self.chunks = []
            self.matrix = None
            return
        data = json.loads(self.persist_path.read_text(encoding="utf-8"))
        self.chunks = [TextChunk(**item) for item in data]
        if self.chunks:
            corpus = [chunk.content for chunk in self.chunks]
            self.matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.matrix = None
