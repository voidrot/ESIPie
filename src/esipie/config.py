from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="esipie_")
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
    user_agent_lib_name: str = "ESIPie"
    user_agent_lib_version: str = "0.1.0"
    user_agent_lib_url: str = "https://github.com/voidrot/esipie"

    # ESI API settings
    esi_base_url: str = "https://esi.evetech.net"
    esi_spec_url: str = "https://esi.evetech.net/meta/openapi.json"
    esi_spec_file_path: str | None = None
    esi_compatibility_date: str = "2025-09-30"
    esi_default_language: str = "en-us"
    esi_default_tenant: str = "tranquility"

    # Caching settings
    cache_prefix: str = "esipie"
    cache_redis_url: str = "redis://localhost:6379/0"

    # Misc settings
    cache_client_sync_key_prefix: str = "esipie:esi_client_sync"
    cache_client_async_key_prefix: str = "esipie:esi_client_async"


CONFIG = Config() # type: ignore user is expected to set env vars
