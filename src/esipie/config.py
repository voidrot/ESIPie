from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Client timeout settings (in seconds)
    client_timeout_connect: int = 5
    client_timeout_read: int = 10
    client_timeout_write: int = 10
    client_timeout_pool: int = 5

    # User-Agent information
    user_agent_contact_email: str
    user_agent_app_name: str
    user_agent_app_version: str
    user_agent_url: str | None = None

    # ESI API settings
    esi_base_url: str = "https://esi.evetech.net"
    esi_spec_url: str = "https://esi.evetech.net/meta/openapi.json"
    esi_compatibility_date: str = "2025-09-30"
    esi_default_language: str = "en-us"
    esi_default_tenant: str = "tranquility"

    # Caching settings
    cache_prefix: str = "esipie"
    cache_redis_url: str = "redis://localhost:6379/0"
