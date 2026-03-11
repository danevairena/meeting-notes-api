from app.models.note import MeetingNotesResponse
from app.repositories import notes_repository

# return notes for a specific meeting
def get_notes_by_meeting_id(meeting_id: str) -> MeetingNotesResponse | None:
    return notes_repository.get_notes_by_meeting_id(meeting_id)