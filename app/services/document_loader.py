from pathlib import Path

from pypdf import PdfReader

from app.core.logger import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Load text content from common document formats."""

    def load(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return self._load_text(file_path)
        if suffix == ".pdf":
            return self._load_pdf(file_path)
        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_text(self, file_path: Path) -> str:
        for encoding in ("utf-8", "utf-8-sig", "gbk"):
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("unknown", b"", 0, 1, f"Cannot decode file: {file_path}")

    def _load_pdf(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"\n[Page {index}]\n{text}")
        content = "\n".join(pages)
        if not content.strip():
            logger.warning("PDF has no extractable text: %s", file_path)
        return content
