# domain error when meeting does not exist
class MeetingNotFoundError(Exception):
    def __init__(self, meeting_id: str) -> None:
        self.meeting_id = meeting_id
        super().__init__(f"meeting '{meeting_id}' not found")


# domain error when notes are missing for a meeting
class NotesNotFoundError(Exception):
    def __init__(self, meeting_id: str) -> None:
        self.meeting_id = meeting_id
        super().__init__(f"notes for meeting '{meeting_id}' not found")


# domain error for invalid client requests
class BadRequestError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

# domain error when processing rate limit is exceeded
class RateLimitExceededError(Exception):
    def __init__(self, meeting_id: str, llm: str) -> None:
        super().__init__(f"processing rate limit exceeded for meeting '{meeting_id}' using llm '{llm}'")