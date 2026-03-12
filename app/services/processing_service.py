from app.models.note import MeetingNotesResponse, ActionItem, KeyTakeaway, NextStep, Topic
from app.services import meetings_service
from app.repositories import notes_repository
from app.utils.chunking import chunk_text


# build structured notes payload that matches the notes table schema
def build_notes_payload(meeting_id: str, transcript_chunks: list[str]) -> dict:
    full_text = " ".join(transcript_chunks).strip()

    summary = full_text[:300] if full_text else None

    # create temporary structured notes until llm extraction is integrated
    action_items = [
        ActionItem(
            task="Review generated meeting notes",
            owner=None,
            due_date=None,
        ).model_dump()
    ]

    key_takeaways = [
        KeyTakeaway(
            text="meeting transcript was processed successfully",
        ).model_dump()
    ]

    topics = [
        Topic(
            name="meeting discussion",
        ).model_dump()
    ]

    next_steps = [
        NextStep(
            step="replace mock processing with llm integration",
            owner=None,
            due_date=None,
        ).model_dump()
    ]

    return {
        "meeting_id": meeting_id,
        "summary": summary,
        "action_items": action_items,
        "key_takeaways": key_takeaways,
        "topics": topics,
        "next_steps": next_steps,
        "llm_raw": full_text,
    }

# generate notes from meeting transcript
def process_meeting(meeting_id: str) -> MeetingNotesResponse:
    meeting = meetings_service.get_meeting_by_id(meeting_id)

    # split transcript into overlapping chunks before note generation
    transcript_chunks = chunk_text(meeting.raw_transcript)

    # build structured payload for database upsert
    note_payload = build_notes_payload(meeting_id, transcript_chunks)

    # upsert notes so repeated processing updates the same meeting record
    return notes_repository.upsert_notes(note_payload)