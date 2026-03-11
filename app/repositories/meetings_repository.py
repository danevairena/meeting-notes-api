from app.models.meeting import MeetingResponse


# temporary in-memory meetings store
# this simulates a database for now
MEETINGS = [
    {
        "id": "1",
        "title": "Product sync",
        "raw_transcript": "Discussed roadmap and release timeline",
    },
    {
        "id": "2",
        "title": "Engineering weekly",
        "raw_transcript": "Reviewed bugs and deployment pipeline",
    },
]

# return all meetings from storage
def list_meetings() -> list[MeetingResponse]:
    return [MeetingResponse(**meeting) for meeting in MEETINGS]

# return a meeting by id
def get_meeting_by_id(meeting_id: str) -> MeetingResponse | None:
    for meeting in MEETINGS:
        if meeting["id"] == meeting_id:
            return MeetingResponse(**meeting)

    return None

# save a new meeting
def create_meeting(meeting: dict) -> MeetingResponse:
    MEETINGS.append(meeting)

    return MeetingResponse(**meeting)