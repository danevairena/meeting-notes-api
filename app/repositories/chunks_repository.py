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