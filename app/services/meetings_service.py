from app.models.meeting import MeetingCreate, MeetingResponse

# temporary in-memory meetings store
# this simulates a database for now
MEETINGS = [
    {
        "id": "1", 
        "title": "Product sync", 
        "raw_transcript": "Discussed roadmap and release timeline"
    },
    {
        "id": "2", 
        "title": "Engineering weekly", 
        "raw_transcript": "Reviewed bugs and deployment pipeline"
    },
]

# return all meetings
def list_meetings() -> list[MeetingResponse]:
    return [MeetingResponse(**meeting) for meeting in MEETINGS]

# return a single meeting by id
def get_meeting_by_id(meeting_id: str) -> MeetingResponse | None:
    for meeting in MEETINGS:
        if meeting["id"] == meeting_id:
            return MeetingResponse(**meeting)

    return None

# create a new meeting and return it
def create_meeting(meeting_data: MeetingCreate) -> MeetingResponse:
    next_id = str(len(MEETINGS) + 1)

    meeting = {
        "id": next_id,
        "title": meeting_data.title,
        "raw_transcript": meeting_data.raw_transcript,
    }

    MEETINGS.append(meeting)

    return MeetingResponse(**meeting)