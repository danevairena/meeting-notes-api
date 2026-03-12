from postgrest.exceptions import APIError

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

# return a single meeting by id or none when it does not exist
def get_meeting_by_id(meeting_id: str) -> MeetingResponse | None:
    try:
        response = (
            supabase.table("meetings")
            .select("*")
            .eq("id", meeting_id)
            .single()
            .execute()
        )
    except APIError as exc:
        # return none when no meeting row is found
        if "PGRST116" in str(exc):
            return None
        raise

    return MeetingResponse(**response.data)

# insert a new meeting into database
def create_meeting(meeting: dict) -> MeetingResponse:
    response = supabase.table("meetings").insert(meeting).execute()

    created = response.data[0]

    return MeetingResponse(**created)