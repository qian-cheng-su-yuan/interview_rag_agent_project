import re
from dataclasses import dataclass
from typing import List


@dataclass
class TextChunk:
    chunk_id: str
    source: str
    content: str


class TextSplitter:
    """Split long documents into overlapping chunks for retrieval."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def split(self, text: str, source: str) -> List[TextChunk]:
        text = self.clean_text(text)
        if not text:
            return []

        chunks: List[TextChunk] = []
        start = 0
        index = 1
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    TextChunk(
                        chunk_id=f"{source}::chunk-{index}",
                        source=source,
                        content=chunk_text,
                    )
                )
                index += 1
            if end == len(text):
                break
            start = max(0, end - self.chunk_overlap)
        return chunks
