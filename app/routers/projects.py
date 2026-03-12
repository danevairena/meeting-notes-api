from fastapi import APIRouter, HTTPException, status

from app.models.project import ProjectCreate, ProjectResponse
from app.services import projects_service


# create router instance for project related endpoints
router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


# return a list of all projects
@router.get("/", response_model=list[ProjectResponse])
def list_projects():
    return projects_service.list_projects()


# return a single project by id
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    project = projects_service.get_project_by_id(project_id)

    # raise http error if project does not exist
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    return project


# create a new project
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate):
    return projects_service.create_project(project_data)