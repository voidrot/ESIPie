import warnings

from aiopenapi3 import OpenAPI
from httpx import Client, Timeout

from esipie.config import CONFIG
from esipie.helpers import _build_user_agent
from esipie.openapi_plugins import _load_plugins


def load_esi_spec_sync(
    spec_url: str | None = None,
    compatibility_date: str | None = None,
    user_agent: str | None = None,
    tenant: str | None = None,
    tags: list[str] | None = None,
    operations: list[str] | None = None,
) -> OpenAPI:
    # Suppress pydantic warnings about Field(default=...) usage in generated models
    warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

    if spec_url is None:
        spec_url = CONFIG.esi_spec_url
    if compatibility_date is None:
        compatibility_date = CONFIG.esi_compatibility_date
    if user_agent is None:
        user_agent = _build_user_agent()
    if tenant is None:
        tenant = CONFIG.esi_default_tenant
    if tags is None:
        tags = []
    if operations is None:
        operations = []

    headers = {
        "User-Agent": user_agent,
        "X-Tenant": tenant,
        "X-Compatibility-Date": compatibility_date,
    }

    def session_factory(**kwargs) -> Client:
        kwargs.pop("headers", None)
        return Client(
            headers=headers,
            timeout=Timeout(
                connect=CONFIG.client_timeout_connect,
                read=CONFIG.client_timeout_read,
                write=CONFIG.client_timeout_write,
                pool=CONFIG.client_timeout_pool,
            ),
            http2=True,
            **kwargs,
        )

    return OpenAPI.load_sync(
        url=spec_url,
        session_factory=session_factory,
        plugins=_load_plugins(tags, operations),
        use_operation_tags=True,
    )
