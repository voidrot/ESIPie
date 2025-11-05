from string import capwords
from aiopenapi3 import OpenAPI
from httpx import AsyncClient, Client, Timeout

from esipie.config import Config
from esipie.openapi_plugins import Add304ContentType, MinifySpec, PatchCompatibilityDatePlugin, Trim204ContentType
from . import __title__, __url__, __version__

def _load_plugins(tags: list[str], operations: list[str]):
    return [PatchCompatibilityDatePlugin(), Trim204ContentType(), Add304ContentType(), MinifySpec(tags, operations)]

def pascal_case_string(string: str) -> str:
    # Check if the string contains spaces or hyphens
    if any(c in string for c in (" ", "-")):
        # Replace hyphens with spaces, capitalize each word, and remove spaces
        return capwords(string.replace("-", " ")).replace(" ", "")

    # Return the original string if no spaces or hyphens are present
    return string


def _build_user_agent(config: Config) -> str:
    sanitized_ua_appname = pascal_case_string(config.user_agent_app_name)
    sanitized_appname = pascal_case_string(__title__)
    ua_version = config.user_agent_app_version

    return (
        f"{sanitized_ua_appname}/{ua_version} "
        f"({config.user_agent_contact_email}{f'; +{config.user_agent_url})' if config.user_agent_url else ')'} "
        f"{sanitized_appname}/{__version__} (+{__url__})"
    )


def get_esi_spec_url(config: Config) -> str:
    base_url = config.esi_spec_url
    return f"{base_url}?compatibility_date={config.esi_compatibility_date}"


def _load_openapi_client(
    spec_url: str,
    compatibility_date: str,
    user_agent: str,
    tenant: str,
    spec_data: str,
    tags: list[str],
    operations: list[str],
    config: Config
) -> OpenAPI:
    headers = {
        'User-Agent': user_agent,
        'X-Tenant': tenant,
        'X-Compatibility-Date': compatibility_date
    }

    def session_factory(**kwargs) -> Client:
        kwargs.pop('headers', None)
        return Client(
            headers=headers,
            timeout=Timeout(
                connect=config.client_timeout_connect,
                read=config.client_timeout_read,
                write=config.client_timeout_write,
                pool=config.client_timeout_pool
            ),
            http2=True,
            **kwargs
        )

    return OpenAPI.loads(
        url=spec_url,
        data=spec_data,
        session_factory=session_factory,
        use_operation_tags=True,
        plugins=_load_plugins(tags, operations),
    )

async def _load_openapi_client_async(
    spec_url: str,
    compatibility_date: str,
    user_agent: str,
    tenant: str,
    tags: list[str],
    operations: list[str],
    config: Config
) -> OpenAPI:
    headers = {
        'User-Agent': user_agent,
        'X-Tenant': tenant,
        'X-Compatibility-Date': compatibility_date
    }

    def session_factory(**kwargs) -> AsyncClient:
        kwargs.pop('headers', None)
        return AsyncClient(
            headers=headers,
            timeout=Timeout(
                connect=config.client_timeout_connect,
                read=config.client_timeout_read,
                write=config.client_timeout_write,
                pool=config.client_timeout_pool
            ),
            http2=True,
            **kwargs
        )

    return await OpenAPI.load_async(
        url=spec_url,
        session_factory=session_factory,
        use_operation_tags=True,
        plugins=_load_plugins(tags, operations),
    )
