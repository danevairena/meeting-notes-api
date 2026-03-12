from pydantic import AliasChoices, BaseModel, Field
from typing import Any
from uuid import UUID
from datetime import datetime


# represent a single action item extracted from the meeting
class ActionItem(BaseModel):
    task: str = Field(validation_alias=AliasChoices("task", "text"))
    owner: str | None = None
    due_date: str | None = None

# represent a single next step extracted from the meeting
class NextStep(BaseModel):
    step: str = Field(validation_alias=AliasChoices("step", "text"))
    owner: str | None = None
    due_date: str | None = None

# represent a simple key takeaway entry
class KeyTakeaway(BaseModel):
    text: str

# represent a simple discussion topic entry
class Topic(BaseModel):
    name: str

# shared structured notes fields
class MeetingNotesBase(BaseModel):
    summary: str | None = None
    action_items: list[ActionItem] | None = None
    key_takeaways: list[KeyTakeaway] | None = None
    topics: list[Topic] | None = None
    next_steps: list[NextStep] | None = None
    llm_raw: str | None = None

# schema returned by the api for meeting notes
class MeetingNotesResponse(MeetingNotesBase):
    id: UUID
    meeting_id: UUID
    created_at: datetime