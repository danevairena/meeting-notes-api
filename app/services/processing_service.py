from app.models.note import MeetingNotesResponse
from app.services import meetings_service
from app.services.notes_service import NOTES


# generate notes from meeting transcript
def process_meeting(meeting_id: str) -> MeetingNotesResponse | None:
    meeting = meetings_service.get_meeting_by_id(meeting_id)

    # return none if meeting does not exist
    if meeting is None:
        return None

    transcript = meeting.raw_transcript

    # simulate llm processing of transcript
    generated_notes = f"summary: {transcript[:100]}"

    # store generated notes
    NOTES[meeting_id] = generated_notes

    return MeetingNotesResponse(
        meeting_id=meeting_id,
        notes=generated_notes,
    )