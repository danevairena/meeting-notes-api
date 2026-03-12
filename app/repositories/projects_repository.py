from app.clients.supabase_client import supabase
from app.models.project import ProjectResponse


# return all projects from database ordered by name
def list_projects() -> list[ProjectResponse]:
    response = (
        supabase.table("projects")
        .select("*")
        .order("name")
        .execute()
    )

    projects = response.data or []

    return [ProjectResponse(**project) for project in projects]


# return a single project by id
def get_project_by_id(project_id: str) -> ProjectResponse | None:
    response = (
        supabase.table("projects")
        .select("*")
        .eq("id", project_id)
        .single()
        .execute()
    )

    project = response.data

    if project is None:
        return None

    return ProjectResponse(**project)


# return a single project by name
def get_project_by_name(name: str) -> ProjectResponse | None:
    response = (
        supabase.table("projects")
        .select("*")
        .eq("name", name)
        .single()
        .execute()
    )

    project = response.data

    if project is None:
        return None

    return ProjectResponse(**project)


# create a new project
def create_project(project: dict) -> ProjectResponse:
    response = supabase.table("projects").insert(project).execute()

    created = response.data[0]

    return ProjectResponse(**created)