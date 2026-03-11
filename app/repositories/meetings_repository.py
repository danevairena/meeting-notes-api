from app.clients.supabase_client import supabase
from app.models.meeting import MeetingResponse


# return all meetings from database
def list_meetings() -> list[MeetingResponse]:
    response = supabase.table("meetings").select("*").execute()

    meetings = response.data or []

    return [MeetingResponse(**meeting) for meeting in meetings]

# return a meeting by id
def get_meeting_by_id(meeting_id: str) -> MeetingResponse | None:
    response = (
        supabase.table("meetings")
        .select("*")
        .eq("id", meeting_id)
        .single()
        .execute()
    )

    meeting = response.data

    if meeting is None:
        return None

    return MeetingResponse(**meeting)

# insert a new meeting into database
def create_meeting(meeting: dict) -> MeetingResponse:
    response = supabase.table("meetings").insert(meeting).execute()

    created = response.data[0]

    return MeetingResponse(**created)