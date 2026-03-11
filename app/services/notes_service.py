from app.models.note import MeetingNotesResponse


# temporary notes storage
# this will later be replaced with database persistence
NOTES = {
    "1": "Discussed roadmap and release timeline",
    "2": "Reviewed bugs and deployment pipeline",
}

# return notes for a specific meeting
def get_notes_by_meeting_id(meeting_id: str) -> MeetingNotesResponse | None:
    notes = NOTES.get(meeting_id)

    if notes is None:
        return None

    return MeetingNotesResponse(
        meeting_id=meeting_id,
        notes=notes,
    )