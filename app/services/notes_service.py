from app.models.note import MeetingNotesResponse
from app.repositories import notes_repository

# return all generated note versions for a meeting
def list_notes_by_meeting_id(meeting_id: str) -> list[MeetingNotesResponse]:
    return notes_repository.list_notes_by_meeting_id(meeting_id)