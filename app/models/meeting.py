from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


# base meeting schema shared by multiple models
class MeetingBase(BaseModel):
    title: str
    meeting_date: date
    source: str
    source_file: str
    raw_transcript: str
    project_id: Optional[UUID] = None

# schema used when creating a new meeting
class MeetingCreate(MeetingBase):
    pass

# schema used when returning a meeting from the api
class MeetingResponse(MeetingBase):
    id: UUID
    created_at: datetime