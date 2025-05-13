from supabase import create_client, Client
from .config import settings

supabase: Client | None = None

def get_db() -> Client:
    global supabase
    if supabase is None:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase