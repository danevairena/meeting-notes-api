from pydantic import BaseModel


# base meeting schema shared by multiple models
class MeetingBase(BaseModel):
    title: str
    raw_transcript: str

# schema used when creating a new meeting
class MeetingCreate(MeetingBase):
    pass

# schema used when returning a meeting from the api
class MeetingResponse(MeetingBase):
    id: str