from app.models.note import MeetingNotesResponse
from app.clients.supabase_client import supabase


# return notes for a specific meeting from database
def get_notes_by_meeting_id(meeting_id: str) -> MeetingNotesResponse | None:
    response = (
        supabase.table("notes")
        .select("*")
        .eq("meeting_id", meeting_id)
        .single()
        .execute()
    )

    note = response.data

    # return none when no notes record exists
    if note is None:
        return None

    return MeetingNotesResponse(**note)

# insert or update notes for a specific meeting and llm provider
def upsert_notes(note_payload: dict) -> MeetingNotesResponse:
    response = (
        supabase.table("notes")
        .upsert(note_payload, on_conflict="meeting_id,llm")
        .execute()
    )

    saved_note = response.data[0]

    return MeetingNotesResponse(**saved_note)

# return all generated note versions for a meeting across different llm providers
def list_notes_by_meeting_id(meeting_id: str) -> list[MeetingNotesResponse]:
    response = (
        supabase.table("notes")
        .select("*")
        .eq("meeting_id", meeting_id)
        .execute()
    )

    notes = response.data or []

    return [MeetingNotesResponse(**note) for note in notes]