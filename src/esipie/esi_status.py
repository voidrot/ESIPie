import httpx
from pydantic import BaseModel

from esipie.config import CONFIG


class EsiRouteStatus(BaseModel):
    """Model for individual ESI route status."""

    method: str
    path: str
    status: str


def get_esi_status() -> list[EsiRouteStatus]:
    """Get the current ESI status from the EVE Online status page."""

    status_url = f"https://esi.evetech.net/meta/status?tenant={CONFIG.esi_default_tenant}&compatibility_date={CONFIG.esi_compatibility_date}"
    try:
        data = []
        response = httpx.get(status_url, timeout=5)
        response.raise_for_status()
        status_data = response.json()
        for route in status_data.get("routes", []):
            item = EsiRouteStatus.model_validate(route)  # Validate data
            data.append(item)
        return data
    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to fetch ESI status: {e}") from e
