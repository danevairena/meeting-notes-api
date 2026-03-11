from app.models.note import MeetingNotesResponse


# temporary notes storage
NOTES = {
    "1": "Discussed roadmap and release timeline",
    "2": "Reviewed bugs and deployment pipeline",
}

# return notes by meeting id
def get_notes_by_meeting_id(meeting_id: str) -> MeetingNotesResponse | None:
    notes = NOTES.get(meeting_id)

    if notes is None:
        return None

    return MeetingNotesResponse(
        meeting_id=meeting_id,
        notes=notes,
    )

# save generated notes
def save_notes(meeting_id: str, notes: str) -> MeetingNotesResponse:
    NOTES[meeting_id] = notes

    return MeetingNotesResponse(
        meeting_id=meeting_id,
        notes=notes,
    )