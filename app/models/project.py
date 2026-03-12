from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# shared project fields
class ProjectBase(BaseModel):
    name: str

# schema used when creating a project
class ProjectCreate(ProjectBase):
    pass

# schema returned by the api
class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime