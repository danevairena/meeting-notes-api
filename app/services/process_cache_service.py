from datetime import datetime, timedelta, timezone

from app.models.note import MeetingNotesResponse


# keep recently generated notes in memory to avoid repeated expensive llm processing
_process_cache: dict[str, tuple[datetime, dict]] = {}

# track the last processing attempt per meeting and llm pair
_last_process_call: dict[str, datetime] = {}

# keep cached results for a short time
CACHE_TTL_SECONDS = 300

# block repeated processing attempts for a short cooldown window
RATE_LIMIT_SECONDS = 30


# build a stable cache key for a meeting and llm provider
def _build_key(meeting_id: str, llm: str) -> str:
    return f"{meeting_id}:{llm}"


# return cached notes when the cache entry is still fresh
def get_cached_notes(meeting_id: str, llm: str) -> MeetingNotesResponse | None:
    key = _build_key(meeting_id, llm)
    cached = _process_cache.get(key)

    if cached is None:
        return None

    cached_at, payload = cached
    expires_at = cached_at + timedelta(seconds=CACHE_TTL_SECONDS)

    if datetime.now(timezone.utc) >= expires_at:
        _process_cache.pop(key, None)
        return None

    return MeetingNotesResponse(**payload)


# store the latest generated notes in the in-memory cache
def set_cached_notes(
    meeting_id: str,
    llm: str,
    notes: MeetingNotesResponse,
) -> None:
    key = _build_key(meeting_id, llm)
    _process_cache[key] = (
        datetime.now(timezone.utc),
        notes.model_dump(mode="json"),
    )


# check whether a new processing request is allowed
def is_rate_limited(meeting_id: str, llm: str) -> bool:
    key = _build_key(meeting_id, llm)
    last_called_at = _last_process_call.get(key)

    if last_called_at is None:
        return False

    allowed_at = last_called_at + timedelta(seconds=RATE_LIMIT_SECONDS)

    return datetime.now(timezone.utc) < allowed_at


# mark the current processing attempt time
def mark_process_call(meeting_id: str, llm: str) -> None:
    key = _build_key(meeting_id, llm)
    _last_process_call[key] = datetime.now(timezone.utc)