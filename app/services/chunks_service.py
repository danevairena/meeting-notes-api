from app.repositories import chunks_repository


# return stored transcript chunks for a meeting
def list_chunks_by_meeting_id(meeting_id: str) -> list[dict]:
    return chunks_repository.list_chunks_by_meeting_id(meeting_id)