from app.clients.supabase_client import supabase


# replace existing transcript chunks for a meeting with a new chunk set
def replace_chunks(meeting_id: str, chunks: list[str]) -> None:

    # remove existing chunks for this meeting
    supabase.table("transcript_chunks").delete().eq("meeting_id", meeting_id).execute()

    if not chunks:
        return

    rows = [
        {
            "meeting_id": meeting_id,
            "chunk_index": i,
            "content": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]

    # insert new chunk set
    supabase.table("transcript_chunks").insert(rows).execute()

# return stored transcript chunks for a meeting ordered by chunk index
def list_chunks_by_meeting_id(meeting_id: str) -> list[dict]:
    response = (
        supabase.table("transcript_chunks")
        .select("*")
        .eq("meeting_id", meeting_id)
        .order("chunk_index")
        .execute()
    )

    return response.data or []