from pydantic import BaseModel


# base meeting schema shared by multiple models
class MeetingBase(BaseModel):
    title: str

# schema used when returning a meeting from the api
class MeetingResponse(MeetingBase):
    id: str