class MeetingNotFoundError(Exception):
    # store missing meeting identifier for error reporting
    def __init__(self, meeting_id: str) -> None:
        self.meeting_id = meeting_id
        super().__init__(f"meeting '{meeting_id}' not found")