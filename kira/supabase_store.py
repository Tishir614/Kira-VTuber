from .config import settings

class SupabaseStore:
    def __init__(self):
        self.client = None
        if settings.supabase_url and settings.supabase_publishable_key:
            try:
                from supabase import create_client
                self.client = create_client(settings.supabase_url, settings.supabase_publishable_key)
            except Exception:
                self.client = None

    @property
    def enabled(self) -> bool:
        return self.client is not None

store = SupabaseStore()
