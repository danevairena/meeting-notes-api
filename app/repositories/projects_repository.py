from postgrest.exceptions import APIError

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


# return a project by name or none when it does not exist
def get_project_by_name(name: str) -> ProjectResponse | None:
    try:
        response = (
            supabase.table("projects")
            .select("*")
            .eq("name", name)
            .single()
            .execute()
        )
    except APIError as exc:
        # return none when no project row is found
        if "PGRST116" in str(exc):
            return None
        raise

    return ProjectResponse(**response.data)


# create a new project
def create_project(project: dict) -> ProjectResponse:
    response = supabase.table("projects").insert(project).execute()

    created = response.data[0]

    return ProjectResponse(**created)