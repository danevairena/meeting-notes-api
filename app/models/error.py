from pydantic import BaseModel


# standardized api error response schema
class ErrorResponse(BaseModel):
    error: str
    message: str