from pydantic import BaseModel


# schema representing generated meeting notes
class MeetingNotesResponse(BaseModel):
    meeting_id: str
    notes: str