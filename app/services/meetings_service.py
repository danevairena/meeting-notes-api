from app.errors import MeetingNotFoundError
from app.models.meeting import MeetingCreate, MeetingListResponse, MeetingResponse
from app.repositories import meetings_repository
from app.services import notes_service


# return all meetings with optional project filter
def list_meetings(project_id: str | None = None) -> list[MeetingListResponse]:
    meetings = meetings_repository.list_meetings(project_id=project_id)

    response: list[MeetingListResponse] = []

    for meeting in meetings:
        # check whether notes exist for the current meeting
        notes = notes_service.list_notes_by_meeting_id(str(meeting.id))

        response.append(
            MeetingListResponse(
                id=meeting.id,
                title=meeting.title,
                meeting_date=meeting.meeting_date,
                source=meeting.source,
                source_file=meeting.source_file,
                source_url=meeting.source_url,
                external_id=meeting.external_id,
                project_id=meeting.project_id,
                created_at=meeting.created_at,
                has_notes=bool(notes),
            )
        )

    return response

# return a single meeting by id
def get_meeting_by_id(meeting_id: str) -> MeetingResponse:
    meeting = meetings_repository.get_meeting_by_id(meeting_id)

    # raise domain error when meeting does not exist
    if meeting is None:
        raise MeetingNotFoundError(meeting_id)

    return meeting

# create a new meeting and return it
def create_meeting(meeting_data: MeetingCreate) -> MeetingResponse:
    # convert pydantic model into json-safe payload for supabase
    meeting_payload = meeting_data.model_dump(mode="json")

    # persist meeting through repository and let database generate id and created_at
    return meetings_repository.create_meeting(meeting_payload)