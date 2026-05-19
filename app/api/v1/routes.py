from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.document import DocumentIndexResponse, UploadDocumentResponse
from app.schemas.qa import AskRequest, AskResponse, KeywordResponse, RecentLogItem, SummaryResponse, ToolRequest
from app.services.agent_tools import AgentTools
from app.services.rag_service import RAGService
from app.utils.file_utils import is_allowed_file, safe_filename

router = APIRouter(prefix="/api/v1", tags=["rag-agent"])
rag_service = RAGService()
agent_tools = AgentTools(rag_service.llm_client)


@router.post("/documents/upload", response_model=UploadDocumentResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadDocumentResponse:
    if not file.filename or not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only TXT, MD and PDF files are supported.")

    filename = safe_filename(file.filename)
    save_path = settings.upload_dir / filename
    content = await file.read()
    save_path.write_bytes(content)

    chunk_count = rag_service.index_single_file(save_path)
    return UploadDocumentResponse(
        message="Document uploaded and indexed successfully.",
        filename=filename,
        saved_path=str(save_path),
        chunk_count=chunk_count,
    )


@router.post("/documents/rebuild", response_model=DocumentIndexResponse)
def rebuild_documents() -> DocumentIndexResponse:
    file_count, chunk_count = rag_service.rebuild_index()
    return DocumentIndexResponse(
        message="Knowledge base index rebuilt successfully.",
        file_count=file_count,
        chunk_count=chunk_count,
    )


@router.post("/qa/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    return rag_service.ask(payload.question, top_k=payload.top_k)


@router.post("/tools/summarize", response_model=SummaryResponse)
def summarize(payload: ToolRequest) -> SummaryResponse:
    return SummaryResponse(summary=agent_tools.summarize(payload.text))


@router.post("/tools/keywords", response_model=KeywordResponse)
def keywords(payload: ToolRequest) -> KeywordResponse:
    return KeywordResponse(keywords=agent_tools.extract_keywords(payload.text))


@router.get("/logs/recent", response_model=list[RecentLogItem])
def recent_logs(limit: int = 10) -> list[RecentLogItem]:
    items = rag_service.read_recent_logs(limit=limit)
    return [RecentLogItem(**item) for item in items]
