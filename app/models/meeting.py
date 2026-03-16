from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# base meeting schema shared by all meeting flows
class MeetingBase(BaseModel):
    title: str
    meeting_date: date
    source: str
    raw_transcript: str
    project_id: Optional[UUID] = None


# schema used when creating a new meeting
class MeetingCreate(MeetingBase):
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    external_id: Optional[str] = None


# schema used when returning a meeting from the api
class MeetingResponse(MeetingBase):
    id: UUID
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime

# schema used when returning meetings list with notes availability
class MeetingListResponse(BaseModel):
    id: UUID
    title: str
    meeting_date: date
    source: str
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    external_id: Optional[str] = None
    project_id: Optional[UUID] = None
    created_at: datetime
    has_notes: bool