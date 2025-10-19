from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UAConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ESIPIE_UA_",
        env_ignore_empty=True,
    )

    app_name: str = Field(
        description="The name of the application for User-Agent header.",
        frozen=True,
    )
    app_version: str = Field(
        description="The version of the application for User-Agent header.",
        frozen=True,
    )
    contact_email: str = Field(
        description="The contact email for the application.",
        frozen=True,
    )

class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ESIPIE_",
        env_ignore_empty=True,
    )

    base_url: str = Field(
        default="https://esi.evetech.net",
        description="The base URL for the ESI API.",
        frozen=True,
    )

    timeout_seconds: int = Field(
        default=10,
        description="The timeout in seconds for API requests.",
        frozen=True,
    )

    compatibility_date: str = Field(
        default="2025-09-26",
        description="The ESI compatibility date to use in requests.",
    )

class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ESIPIE_",
        env_ignore_empty=True,
    )

    sso_client_id: str = Field(
        description="The client ID for EVE SSO authentication.",
        frozen=True,
    )
    sso_client_secret: str = Field(
        description="The client secret for EVE SSO authentication.",
        frozen=True,
    )
    openapi_url: str = Field(
        default="https://esipie.api.esi.evetech.net/openapi.json",
        description="The URL of the ESI OpenAPI specification.",
        frozen=True,
    )
    client_tenant: str = Field(
        default="tranquility",
        description="The EVE Online client tenant to use.",
        frozen=True,
    )

class CacheConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ESIPIE_",
        env_ignore_empty=True,
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="The Redis URL for caching.",
        frozen=True,
    )

    spec_cache_duration: int = Field(
        default=3600,
        description="The duration in seconds to cache the ESI OpenAPI spec.",
    )

    disable_cache: bool = Field(
        default=False,
        description="Flag to disable caching entirely.",
    )

    cache_prefix: str = Field(
        default="esipie",
        description="The prefix to use for cache keys in Redis.",
        frozen=True,
    )

class Config(BaseSettings):
    api: APIConfig = Field(default_factory=APIConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    ua: UAConfig = Field(default_factory=UAConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)


