from hashlib import blake2b
from typing import Any
from aiopenapi3 import OpenAPI
from httpx import (
    AsyncClient, Client, HTTPStatusError, RequestError, Response, Timeout,
)
import httpx
import redis
from esipie.config import Config
from esipie.custom_types import Token
from aiopenapi3._types import ResponseDataType, ResponseHeadersType
import logging
import pickle

logger = logging.getLogger(__name__)

DEFAULT_EXPIRY = 60 * 60 * 24 * 5  # 5 days

class BaseEsiClient:
    def __init__(self, operation, api: OpenAPI) -> None:
        self.method, self.url, self.operation, self.extra = operation
        self.api = api
        self.token: Token | None = None
        self.config = Config() # type: ignore we expect the user to correctly set the required env vars
        self.cache = redis.Redis.from_url(self.config.cache_redis_url)
        self._kwargs = {}

    def __call__(self, *args, **kwargs) -> 'BaseEsiClient':
        self._args = args
        self._kwargs = kwargs
        return self

    def _unnormalize_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize caller-supplied parameter keys to the names defined by the operation spec.

        This method takes a dict of parameters provided by a caller and returns a new dict
        whose keys are mapped to the parameter names declared on self.operation (if any).
        Mapping rules, evaluated in order for each input key:
        - Exact match: if the input key exactly equals a spec name, keep that spec name.
        - Hyphen variant: replace underscores in the input key with hyphens and try an exact match.
        - Case-insensitive match: try a case-insensitive match against spec names.
        - Case-insensitive hyphen variant: try the hyphenated key case-insensitively.
        - Fallback: if none of the above match, keep the input key unchanged (validation is deferred
            to the downstream aiopenapi3 library).

        Args:
                params: Dict[str, Any] of parameter names (possibly using different casing or underscores)
                        to values provided by the caller.

        Returns:
                Dict[str, Any] mapping parameter names to values where keys were translated to the
                corresponding names from the operation specification when a match was found; unknown
                keys are preserved verbatim.

        Notes:
        - The operation parameter names are obtained from self.operation.parameters when available;
            if that access fails, the function behaves as if no spec parameters exist (i.e., it will
            return a shallow copy of the input dict).
        - If multiple spec names only differ by case, the first encountered name in the spec is used
            for case-insensitive matches.
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

    def _etag_cache_key(self) -> str:
        """Return the cache key used to store this resource's ETag.

        This private helper builds a stable key for the cache backend by
        appending a fixed ":etag" suffix to this instance's base cache key.
        The resulting string is intended to be used when storing or retrieving
        the HTTP ETag associated with the resource represented by this client.

        Returns:
            str: A unique cache key identifying the ETag entry for this resource.
        """

        return f'{self._cache_key()}:etag'

    def _data_cache_key(self) -> str:
        """
        Return the cache key used for this object's data.

        This internal helper composes the instance's base cache key (from
        self._cache_key()) with the literal suffix ':data' to produce a stable,
        unique key suitable for storing or retrieving cached data related to this
        object.

        Returns:
            str: The full data cache key, e.g. "<base_key>:data".
        """
        return f'{self._cache_key()}:data'

    def _cache_key(self) -> str:
        """
        Generate a deterministic cache key for this request.

        The cache key is built by:
        - Removing the 'token' entry from self._kwargs (the token can change even when the response is the same).
        - Concatenating self.method, self.url, the string form of self._args, and the string form of the filtered kwargs.
        - Encoding that concatenated string as UTF-8 and hashing it with BLAKE2b (32-byte digest).
        - Prefixing the resulting hex digest with self.config.cache_prefix followed by ':'.

        Returns:
            str: A cache key string suitable for use as a cache identifier.

        Notes:
        - The function relies on the str() representation of args and kwargs. If those contain unordered
          or non-deterministic representations (e.g., sets or objects with unstable __str__/__repr__),
          the resulting key may not be stable across invocations.
        """

        # Ignore the token for generating the cache key. The token can change but the response will not.
        ignore = ['token']
        new_kwargs = {k: v for k, v in self._kwargs.items() if k not in ignore}
        hash_data = (self.method + self.url + str(self._args) + str(new_kwargs)).encode(
            'utf-8'
        )
        hash_str = blake2b(hash_data, digest_size=32).hexdigest()
        return f'{self.config.cache_prefix}:{hash_str}'

    def _extract_body_params(self) -> Token | None:
        """
        Extract and validate a 'body' parameter from the instance kwargs.

        Pops and returns the value associated with the 'body' key from self._kwargs, if present.
        If a body value is provided but the current operation does not declare support for a
        request body (i.e., getattr(self.operation, 'requestBody', False) is falsy), a ValueError
        is raised.

        Returns:
            Token | None: The popped body value, or None if no body was provided.

        Raises:
            ValueError: If a body value was supplied but the operation does not accept a body.

        Side effects:
            Mutates self._kwargs by removing the 'body' entry when present.
        """
        _body = self._kwargs.pop('body', None)
        if _body and not getattr(self.operation, 'requestBody', False):
            raise ValueError('This operation does not accept a body parameter')
        return _body

    def _extract_token_param(self) -> Token | None:
        """
        Extract and validate a token parameter from the instance kwargs.

        This method pops the 'token' entry from self._kwargs (if present) and returns
        the effective token to use for the operation. If an explicit token is set on
        the instance (`self.token`), that value takes precedence and is returned;
        otherwise the popped token from kwargs is returned. If no token is available,
        None is returned.

        Raises:
            ValueError: If a token was provided via kwargs but the current operation
                does not accept a token (i.e., the operation's `security` attribute
                is falsy).

        Side effects:
            The 'token' key is removed from self._kwargs when present.

        Returns:
            Token | None: The token to use for the request, or None if none is supplied.
        """
        _token = self._kwargs.pop('token', None)
        if _token and not getattr(self.operation, 'security', False):
            raise ValueError('This operation does not accept a token parameter')
        return self.token or _token

    def _has_page_param(self) -> bool:
        """Return whether the associated operation declares a 'page' parameter.

        Checks the operation's parameters for any parameter whose name is exactly "page"
        (case-sensitive). Useful for determining if pagination is supported by the
        operation.

        Returns:
            bool: True if a parameter named "page" is present in self.operation.parameters,
            False otherwise.

        Notes:
            Expects self.operation.parameters to be an iterable of objects with a 'name'
            attribute (e.g., parameter model instances or simple namespaces).
        """

        return any(p.name == "page" for p in self.operation.parameters)

    def _has_cursor_param(self) -> bool:
        """
        Return whether the associated operation exposes a cursor-style pagination parameter.

        Checks self.operation.parameters for any parameter with the exact name "before" or "after".
        This is used to detect cursor-based pagination support for the operation.

        Returns:
            bool: True if at least one parameter named exactly "before" or "after" exists;
                  otherwise False.

        Notes:
            - Comparison is case-sensitive.
            - Expects self.operation.parameters to be an iterable of objects with a `name` attribute.
        """

        return any(p.name == "before" or p.name == "after" for p in self.operation.parameters)

    def _store_etag(self, etag: str | dict) -> None:
        etag_value: str | None = None
        if isinstance(etag, dict):
            etag_value = etag.get("ETag") or etag.get("etag")
            if not etag_value:
                raise ValueError("ETag dictionary must contain 'ETag' or 'etag' key")
        # Ensure we store a plain string (redis-py accepts str/bytes/numbers); cast other types to str
        value_to_store = etag_value if etag_value is not None else str(etag)
        self.cache.set(self._etag_cache_key(), value_to_store, ex=DEFAULT_EXPIRY)

    def _remove_etag(self) -> None:
        try:
            self.cache.delete(self._etag_cache_key())
            logger.debug('Deleted ETag cache for key %s', self._etag_cache_key())
        except Exception as e:
            logger.error('Error deleting etag cache: %s', e, exc_info=True)  # noqa: G201

    def _store_response(self, cache_key: str, response: Response) -> None:
        try:
            self.cache.set(cache_key, pickle.dumps(response), ex=DEFAULT_EXPIRY)
        except Exception as e:
            logger.error(  # noqa: G201
                'Error setting response cache for key %s: %s',
                cache_key,
                e,
                exc_info=True,
            )

    def parse_cached_response(
        self, cached_response: Response
    ) -> tuple[ResponseHeadersType, ResponseDataType]:
        """
        Parse a cached HTTP response using the operation's request processor.

        This method recreates the Request object for the current operation (using
        self.api.createRequest with the operation's primary tag and operationId)
        and delegates processing of the provided cached_response to the Request
        implementation's _process_request method. It performs the same
        validation/deserialization/header extraction as a live request would, but
        does not perform any network I/O.

        Args:
            cached_response (Response): A cached response object (e.g., a
                requests.Response or framework-specific response) that is suitable
                for consumption by the underlying Request._process_request method.

        Returns:
            tuple[ResponseHeadersType, ResponseDataType]: A tuple containing the
            processed response headers and the deserialized response data.

        Raises:
            IndexError: If operation.tags is empty when attempting to access the
                primary tag.
            AttributeError: If required attributes (operation.operationId, api.createRequest,
                or Request._process_request) are missing.
            Any exceptions raised by api.createRequest or Request._process_request
                (for example validation or deserialization errors) are propagated.

        Notes:
            - This is a convenience helper to reuse the request-processing logic
              against responses obtained from a cache or other non-network source.
            - It relies on a private method (_process_request) of the Request
              object; callers should be aware this may be considered internal API.
        """
        req = self.api.createRequest(
            f'{self.operation.tags[0]}.{self.operation.operationId}'
        )
        return req._process_request(cached_response)

    def _get_cache(self, cache_key: str, etag: str | None) -> tuple[ResponseHeadersType | None, Any, Response | None]:
        """
        Retrieve and validate a cached response for a given cache key and optional ETag.

        This function attempts to fetch an entry from the configured cache using
        `cache_key`. If a cached entry is found and an `etag` is provided, the function
        compares the provided ETag to the cached entry's "ETag" header. If the ETag
        matches, the cached entry is parsed via `self.parse_cached_response` and the
        parsed headers, parsed data, and the raw cached response object are returned.

        If the cache backend raises an exception while accessing the key, the error is
        logged and the function returns (None, None, None). If there is no cached entry
        or the ETag does not match, the function logs a cache miss and returns
        (None, None, None).

        Parameters
        ----------
        cache_key : str
            The key used to look up the cached response.
        etag : str | None
            Optional ETag value to validate against the cached entry's "ETag" header.
            When None, the function does not return cached content (treated as a miss).

        Returns
        -------
        tuple[ResponseHeadersType | None, Any, Response | None]
            A tuple of (headers, data, cached_response):
            - headers: Parsed response headers from the cache, or None if no usable cache.
            - data: Parsed cached payload, or None if no usable cache.
            - cached_response: The raw cached Response-like object, or None if no usable cache.

        Notes
        -----
        - Cache access errors are caught and logged; they do not raise from this method.
        - The cached object is expected to expose a `headers` mapping with an "ETag" key.
        - Parsed headers and data are produced by `self.parse_cached_response(cached_data)`.
        """
        try:
            pickled_data = self.cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Error accessing cache for key {cache_key}: {e}")
            return None, None, None

        cached_data: Response | None = pickle.loads(pickled_data) if pickled_data else None # type: ignore

        if cached_data:
            logger.debug(f"Cache hit for key {cache_key}")
            if etag:
                if cached_data.headers.get("ETag") == etag: # type: ignore redis types are bad
                    logger.debug(f"ETag matches for key {cache_key}, returning cached response")
                    headers, data = self.parse_cached_response(cached_data) # type: ignore
                    return headers, data, cached_data # type: ignore
        logger.debug(f"Cache miss for key {cache_key}")
        return None, None, None
