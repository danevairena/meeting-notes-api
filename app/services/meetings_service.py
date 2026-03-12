from app.errors import MeetingNotFoundError
from app.models.meeting import MeetingCreate, MeetingResponse
from app.repositories import meetings_repository

# return all meetings
def list_meetings() -> list[MeetingResponse]:
    return meetings_repository.list_meetings()

# return a single meeting by id
def get_meeting_by_id(meeting_id: str) -> MeetingResponse:
    meeting = meetings_repository.get_meeting_by_id(meeting_id)

    # raise domain error when meeting does not exist
    if meeting is None:
        raise MeetingNotFoundError(meeting_id)

    return meeting

# create a new meeting and return it
def create_meeting(meeting_data: MeetingCreate) -> MeetingResponse:
    meeting_payload = meeting_data.model_dump()

    # persist meeting through repository and let database generate id and created_at
    return meetings_repository.create_meeting(meeting_payload)