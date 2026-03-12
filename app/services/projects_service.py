from app.models.project import ProjectCreate, ProjectResponse
from app.repositories import projects_repository


# return all projects
def list_projects() -> list[ProjectResponse]:
    return projects_repository.list_projects()


# return a single project by id
def get_project_by_id(project_id: str) -> ProjectResponse | None:
    return projects_repository.get_project_by_id(project_id)


# create a new project
def create_project(project_data: ProjectCreate) -> ProjectResponse:
    project_payload = project_data.model_dump()

    return projects_repository.create_project(project_payload)


# return existing project or create a new one when it does not exist
def get_or_create_project(name: str) -> ProjectResponse:
    project = projects_repository.get_project_by_name(name)

    if project is not None:
        return project

    return projects_repository.create_project({"name": name})