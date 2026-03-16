from typing import Literal
from uuid import UUID

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
    google_doc_url: HttpUrl
    success: bool
    meeting_id: UUID | None = None
    error: str | None = None


class GoogleDocsImportResponse(BaseModel):
    # bulk import response summary
    total: int
    imported: int
    failed: int
    results: list[GoogleDocsImportItemResult] = Field(default_factory=list)

class GoogleDocsImportJobResponse(BaseModel):
    # response returned when a background import job is created
    job_id: str
    status: Literal["pending", "processing", "completed", "completed_with_errors", "failed"]

class GoogleDocsImportJobStatusResponse(BaseModel):
    # detailed job status returned when polling a background import job
    job_id: str
    status: Literal["pending", "processing", "completed", "completed_with_errors", "failed"]

    # total meetings included in the import request
    total: int = 0

    # number of successfully imported meetings
    imported: int = 0

    # number of failed meeting imports
    failed: int = 0

    # per-item results for the completed job
    results: list[GoogleDocsImportItemResult] = Field(default_factory=list)

    # optional job-level error when the entire job fails
    error: str | None = None