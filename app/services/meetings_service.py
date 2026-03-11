# temporary in-memory meetings store
# this simulates a database for now
MEETINGS = [
    {"id": "1", "title": "Product sync"},
    {"id": "2", "title": "Engineering weekly"},
]

# return all meetings
def list_meetings():
    return MEETINGS

# return a single meeting by id
def get_meeting_by_id(meeting_id: str):
    for meeting in MEETINGS:
        if meeting["id"] == meeting_id:
            return meeting

    return None