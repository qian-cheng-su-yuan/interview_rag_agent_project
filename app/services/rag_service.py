import json
import time
from datetime import datetime
from pathlib import Path
from typing import List

from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.qa import AskResponse, SourceChunk
from app.services.document_loader import DocumentLoader
from app.services.llm_client import LLMClient
from app.services.text_splitter import TextChunk, TextSplitter
from app.services.vector_store import LocalVectorStore
from app.utils.file_utils import list_supported_files

logger = get_logger(__name__)


class RAGService:
    """Coordinate document indexing, retrieval and answer generation."""

    def __init__(self) -> None:
        self.loader = DocumentLoader()
        self.splitter = TextSplitter(settings.chunk_size, settings.chunk_overlap)
        self.vector_store = LocalVectorStore(settings.chunk_store_path)
        self.llm_client = LLMClient()

    def rebuild_index(self, folders: List[Path] | None = None) -> tuple[int, int]:
        folders = folders or [settings.knowledge_base_dir, settings.upload_dir]
        all_chunks: List[TextChunk] = []
        file_count = 0

        for folder in folders:
            for file_path in list_supported_files(folder):
                try:
                    text = self.loader.load(file_path)
                    chunks = self.splitter.split(text, source=file_path.name)
                    all_chunks.extend(chunks)
                    file_count += 1
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Failed to load file %s: %s", file_path, exc)

        self.vector_store.build(all_chunks)
        return file_count, len(all_chunks)

    def index_single_file(self, file_path: Path) -> int:
        text = self.loader.load(file_path)
        chunks = self.splitter.split(text, source=file_path.name)
        self.vector_store.add_and_rebuild(chunks)
        return len(chunks)

    def ask(self, question: str, top_k: int | None = None) -> AskResponse:
        started = time.time()
        top_k = top_k or settings.top_k
        results = self.vector_store.search(question, top_k=top_k)
        sources = [SourceChunk(**item) for item in results]

        if not sources:
            answer = "知识库中没有检索到足够相关的内容，暂时无法基于资料给出确定回答。"
            used_llm = False
        else:
            context = "\n\n".join(
                [f"[{idx}] 来源：{item.source}\n{item.content}" for idx, item in enumerate(sources, start=1)]
            )
            messages = self._build_prompt(question, context)
            answer, used_llm = self.llm_client.chat(messages)

        elapsed_ms = int((time.time() - started) * 1000)
        response = AskResponse(
            question=question,
            answer=answer,
            sources=sources,
            elapsed_ms=elapsed_ms,
            used_llm=used_llm,
        )
        self._write_qa_log(response)
        return response

    def _build_prompt(self, question: str, context: str) -> list[dict]:
        system_prompt = (
            "你是企业知识库 AI Agent。回答必须优先依据知识库片段。"
            "如果资料中没有明确依据，要直接说明无法确定，不能编造。"
            "回答应结构清晰，可使用条目。"
        )
        user_prompt = f"""
【用户问题】
{question}

【知识库片段】
{context}

请基于以上资料回答用户问题，并尽量指出依据来自哪些片段。
""".strip()
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _write_qa_log(self, response: AskResponse) -> None:
        settings.qa_log_path.parent.mkdir(parents=True, exist_ok=True)
        item = {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": response.question,
            "answer": response.answer[:1000],
            "elapsed_ms": response.elapsed_ms,
            "source_count": len(response.sources),
            "used_llm": response.used_llm,
        }
        with settings.qa_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def read_recent_logs(self, limit: int = 10) -> list[dict]:
        if not settings.qa_log_path.exists():
            return []
        lines = settings.qa_log_path.read_text(encoding="utf-8").splitlines()[-limit:]
        items = []
        for line in lines:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return list(reversed(items))
