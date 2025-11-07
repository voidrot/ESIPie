from typing import Any

import redis
from aiopenapi3 import OpenAPI
from redis import Redis

from esipie.config import CONFIG


class BaseEsiOperation:
    def __init__(self, operation, api: OpenAPI):
        self.method, self.url, self.operation, self.extra = operation
        self.api = api
        self.token: str | None = None
        self.cache: Redis = redis.Redis.from_url(CONFIG.cache_redis_url)

    def __call__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        return self

    def _unnormalize_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """UN-Normalize Pythonic parameter names back to OpenAPI names.

        Converts pythonic keys like "Accept_Language" to "Accept-Language" when/if
        a non pythonic (usually) hyphenated form exists in the operation's parameter list. Performs
        case-insensitive matching and only rewrites when there's a known
        parameter with hyphens, leaving normal snake_case params (e.g.
        "type_id") untouched.
        Args:
            params: Raw parameters collected from the call
        Returns:
            dict: Parameters with keys aligned to the OpenAPI spec
        """
        try:
            spec_param_names = [p.name for p in getattr(self.operation, "parameters", [])]
        except Exception:
            spec_param_names = []

        # Exact and case-insensitive lookup maps
        spec_param_set = set(spec_param_names)
        spec_param_map_ci = {n.lower(): n for n in spec_param_names}

        normalized: dict[str, Any] = {}
        for k, v in params.items():
            # Fast path: exact match
            if k in spec_param_set:
                normalized[k] = v
                continue

            # Try hyphen variant
            k_dash = k.replace("_", "-")
            if k_dash in spec_param_set:
                normalized[k_dash] = v
                continue

            # Case-insensitive fallbacks
            kl = k.lower()
            if kl in spec_param_map_ci:
                normalized[spec_param_map_ci[kl]] = v
                continue

            k_dash_l = k_dash.lower()
            if k_dash_l in spec_param_map_ci:
                normalized[spec_param_map_ci[k_dash_l]] = v
                continue

            # Unknown to the spec; pass through as-is (aiopenapi3 will validate)
            normalized[k] = v

        return normalized

    def _extract_body_param(self) -> Any | None:
        """Pop the request body from parameters to be able to check the param validity
        Returns:
            Any | None: the request body
        """
        _body = self._kwargs.pop("body", None)
        if _body and not getattr(self.operation, "requestBody", False):
            raise ValueError("Request Body provided on endpoint with no request body parameter.")
        return _body

    def _extract_token_param(self) -> str | None:
        """Pop token from parameters or use the Client wide token if set
        Returns:
            Token | None: The token to use for the request
        """
        _token = self._kwargs.pop("token", None)
        if _token and not getattr(self.operation, "security", False):
            raise ValueError("Token provided on public endpoint")
        return self.token or _token

    def _has_page_param(self) -> bool:
        """Check if this operation supports Offset Based Pagination.
        Returns:
            bool: True if page parameters are present, False otherwise
        """
        return any(p.name == "page" for p in self.operation.parameters)

    def _has_cursor_param(self) -> bool:
        """Check if this operation supports Cursor Based Pagination.
        Returns:
            bool: True if cursor parameters are present, False otherwise
        """
        return any(p.name == "before" or p.name == "after" for p in self.operation.parameters)
