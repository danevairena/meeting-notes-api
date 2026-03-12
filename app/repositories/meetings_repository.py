from app.clients.supabase_client import supabase
from app.models.meeting import MeetingResponse


# return meetings from database with optional project filter
def list_meetings(project_id: str | None = None) -> list[MeetingResponse]:
    query = supabase.table("meetings").select("*")

    if project_id is not None:
        query = query.eq("project_id", project_id)

    response = query.order("meeting_date", desc=True).execute()

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