from supabase import Client, create_client

from app.settings import settings


# create a single supabase client instance for the whole app
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key,
)