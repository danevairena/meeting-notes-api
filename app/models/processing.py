from pydantic import BaseModel


# request body used to select which llm provider should process the meeting
class ProcessMeetingRequest(BaseModel):
    llm: str