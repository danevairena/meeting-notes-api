from app.models.meeting import MeetingCreate, MeetingResponse
from app.repositories import meetings_repository

# return all meetings
def list_meetings() -> list[MeetingResponse]:
    return meetings_repository.list_meetings()

# return a single meeting by id
def get_meeting_by_id(meeting_id: str) -> MeetingResponse | None:
    return meetings_repository.get_meeting_by_id(meeting_id)

# create a new meeting and return it
def create_meeting(meeting_data: MeetingCreate) -> MeetingResponse:
    existing_meetings = meetings_repository.list_meetings()

    next_id = str(len(existing_meetings) + 1)

    meeting = {
        "id": next_id,
        "title": meeting_data.title,
        "raw_transcript": meeting_data.raw_transcript,
    }

    return meetings_repository.create_meeting(meeting)