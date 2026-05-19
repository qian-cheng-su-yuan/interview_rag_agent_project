from pydantic import BaseModel, Field


class DocumentIndexResponse(BaseModel):
    message: str
    file_count: int = 0
    chunk_count: int = 0


class UploadDocumentResponse(BaseModel):
    message: str
    filename: str
    saved_path: str
    chunk_count: int = Field(default=0, description="Number of chunks after indexing")
