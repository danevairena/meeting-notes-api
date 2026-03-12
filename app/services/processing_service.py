from fastapi import HTTPException

from app.models.note import MeetingNotesResponse
from app.services import meetings_service
from app.repositories import chunks_repository, notes_repository
from app.utils.chunking import chunk_text
from app.services.llm_extraction_service import (
    extract_notes_from_chunk,
    generate_final_summary,
    rewrite_notes,
)


# normalize extracted key takeaways into database shape
def normalize_key_takeaways(items: list[str]) -> list[dict[str, str]]:
    return [{"text": item} for item in items if item.strip()]

# normalize extracted topics into database shape
def normalize_topics(items: list[str]) -> list[dict[str, str]]:
    return [{"name": item} for item in items if item.strip()]

# merge partial notes extracted from transcript chunks
def merge_chunk_notes(chunk_notes: list[dict[str, object]]) -> dict[str, object]:
    summaries: list[str] = []
    action_items: list[dict[str, object]] = []
    key_takeaways: list[str] = []
    topics: list[str] = []
    next_steps: list[dict[str, object]] = []

    for note in chunk_notes:
        summary = note.get("summary")
        if isinstance(summary, str) and summary.strip():
            summaries.append(summary.strip())

        action_items.extend(note.get("action_items") or [])
        key_takeaways.extend(note.get("key_takeaways") or [])
        topics.extend(note.get("topics") or [])
        next_steps.extend(note.get("next_steps") or [])

    return {
        "summaries": summaries,
        "action_items": action_items,
        "key_takeaways": normalize_key_takeaways(key_takeaways),
        "topics": normalize_topics(topics),
        "next_steps": next_steps,
    }

# process a meeting transcript with the selected llm and persist generated notes
def process_meeting(meeting_id: str, llm: str) -> MeetingNotesResponse:
    meeting = meetings_service.get_meeting_by_id(meeting_id)

    # split transcript into chunks
    transcript_chunks = chunk_text(meeting.raw_transcript)

    # remove empty chunks defensively after normalization and splitting
    transcript_chunks = [chunk.strip() for chunk in transcript_chunks if chunk.strip()]

    # replace existing transcript chunks for a meeting with a new chunk set
    chunks_repository.replace_chunks(meeting_id=meeting_id, chunks=transcript_chunks)

    # handle empty transcripts gracefully
    if not transcript_chunks:
        note_payload = {
            "meeting_id": meeting_id,
            "summary": None,
            "action_items": [],
            "key_takeaways": [],
            "topics": [],
            "next_steps": [],
            "llm_raw": "",
            "llm": llm,
        }

        return notes_repository.upsert_notes(note_payload)

    extracted_chunks: list[dict[str, object]] = []
    raw_outputs: list[str] = []
    successful_chunks = 0
    failed_chunks = 0

    for chunk in transcript_chunks:
        try:
            extracted_notes, raw_output = extract_notes_from_chunk(
                transcript=chunk,
                llm=llm,
            )
            extracted_chunks.append(extracted_notes)
            raw_outputs.append(raw_output)
            successful_chunks += 1
        except Exception as exc:
            raw_outputs.append(f"chunk processing failed: {exc}")
            failed_chunks += 1

    # fallback when all chunk extractions fail
    if not extracted_chunks:
        raise HTTPException(
            status_code=503,
            detail="Meeting processing failed. No transcript chunks were processed."
        )

        return notes_repository.upsert_notes(note_payload)

    merged_notes = merge_chunk_notes(extracted_chunks)

    # generate one final summary from all chunk summaries
    final_summary = generate_final_summary(
        summaries=merged_notes["summaries"],
        llm=llm,
    )

    # rewrite merged notes to remove duplicates and noise
    rewritten_notes, rewrite_raw = rewrite_notes(
        notes={
            "summary": final_summary,
            "action_items": merged_notes["action_items"],
            "key_takeaways": [item["text"] for item in merged_notes["key_takeaways"]],
            "topics": [item["name"] for item in merged_notes["topics"]],
            "next_steps": merged_notes["next_steps"],
        },
        llm=llm,
    )

    note_payload = {
        "meeting_id": meeting_id,
        "summary": rewritten_notes.get("summary"),
        "action_items": rewritten_notes.get("action_items"),
        "key_takeaways": normalize_key_takeaways(
            rewritten_notes.get("key_takeaways") or []
        ),
        "topics": normalize_topics(
            rewritten_notes.get("topics") or []
        ),
        "next_steps": rewritten_notes.get("next_steps"),
        "llm_raw": "\n\n".join(raw_outputs + [rewrite_raw]),
        "llm": llm,
    }

    # upsert notes so each meeting and llm pair has one current result
    return notes_repository.upsert_notes(note_payload)