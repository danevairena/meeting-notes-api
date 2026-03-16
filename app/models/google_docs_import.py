from pydantic import BaseModel, Field, HttpUrl


class GoogleDocsImportItem(BaseModel):
    # single meeting import payload item
    title: str = Field(..., min_length=1)
    google_doc_url: HttpUrl


class GoogleDocsImportRequest(BaseModel):
    # bulk import request payload
    meetings: list[GoogleDocsImportItem] = Field(..., min_length=1)


class GoogleDocsImportItemResult(BaseModel):
    # single meeting import result
    title: str
    google_doc_url: str
    success: bool
    meeting_id: str | None = None
    error: str | None = None


class GoogleDocsImportResponse(BaseModel):
    # bulk import response summary
    total: int
    imported: int
    failed: int
    results: list[GoogleDocsImportItemResult]