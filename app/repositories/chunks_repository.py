from app.clients.supabase_client import supabase


def insert_chunks(meeting_id: str, chunks: list[str]) -> None:
    rows = [
        {
            "meeting_id": meeting_id,
            "chunk_index": i,
            "content": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]

    supabase.table("transcript_chunks").insert(rows).execute()