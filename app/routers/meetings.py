from fastapi import APIRouter


# create router instance for meeting related endpoints
router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)

# temporary in-memory meetings store
# this will later be replaced with a database
MEETINGS = [
    {"id": "1", "title": "Product sync"},
    {"id": "2", "title": "Engineering weekly"},
]

# return a list of all meetings
@router.get("/")
def list_meetings():
    return MEETINGS

# return a single meeting by id
@router.get("/{meeting_id}")
def get_meeting(meeting_id: str):
    for meeting in MEETINGS:
        if meeting["id"] == meeting_id:
            return meeting

    return {"error": "meeting not found"}