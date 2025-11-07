from esipie.client import EsiClient
from esipie.config import CONFIG
from esipie.helpers import _build_user_agent
from esipie.spec_loader import load_esi_spec_sync


class EsiClientProvider:
    _client: EsiClient | None = None

    def __init__(
        self,
        spec_url: str | None = None,
        compatibility_date: str | None = None,
        user_agent: str | None = None,
        tenant: str | None = None,
        tags: list[str] | None = None,
        operations: list[str] | None = None,
    ) -> None:
        self._spec_url = spec_url
        self._compatibility_date = compatibility_date
        self._user_agent = user_agent or _build_user_agent()
        self._tenant = tenant
        self._tags = tags
        self._operations = operations

    @property
    def client(self) -> EsiClient:
        if self._client is None:
            api = load_esi_spec_sync(
                spec_url=self._spec_url,
                compatibility_date=self._compatibility_date,
                user_agent=self._user_agent,
                tenant=self._tenant,
                tags=self._tags,
                operations=self._operations,
            )
            self._client = EsiClient(api)
        return self._client

    def __str__(self) -> str:
        return f"ESIClientProvider - {self._user_agent}"
