import logging
from typing import Any

from aiopenapi3.errors import HTTPClientError as base_HTTPClientError
from aiopenapi3.errors import HTTPServerError as base_HTTPServerError
from aiopenapi3.request import RequestBase
from httpx import Response

from esipie.base_esi_operation import BaseEsiOperation
from esipie.exceptions import EsiErrorLimitException, HTTPClientError, HTTPNotModified, HTTPServerError
from esipie.helpers import http_retry_sync
from esipie.http_types import HTTPEsiErrorRateLimit

logger = logging.getLogger(__name__)


class EsiOperation(BaseEsiOperation):
    def _make_request(self, parameters: dict[str, Any], etag: str | None = None) -> RequestBase.Response:
        reset = self.cache.get("esi_rate_limit_reset")
        if reset is not None:
            raise EsiErrorLimitException(reset=reset)

        retry = http_retry_sync()

        def __func():
            req = self.api.createRequest(f"{self.operation.tags[0]}.{self.operation.operationId}")

            if self.token:
                self.api.authenticate(OAuth2=True)
                req.req.headers["Authorization"] = f"Bearer {self.token}"

            if etag:
                req.req.headers["If-None-Match"] = etag

            _response = req.request(data=self.body, parameters=self._unnormalize_parameters(parameters))
            return _response

        return retry(__func)  # type: ignore

    def result(self, return_response: bool = False, force_refresh: bool = False, **extra) -> tuple[Any, Response] | Any:
        self.token = self._extract_token_param()
        self.body = self._extract_body_param()
        parameters = self._kwargs | extra
        etag = None  # TODO: implement ETag caching
        response = None
        headers = None
        data = None

        if force_refresh:
            # TODO: implement cache invalidation
            pass

        # TODO: implement caching logic

        if not response:
            logger.debug(f"Cache Miss {self.url}")
            try:
                headers, data, response = self._make_request(parameters, etag)
            except base_HTTPServerError as e:
                raise HTTPServerError(status_code=e.status_code, headers=e.headers, data=e.data) from e
            except base_HTTPClientError as e:
                if e.status_code == HTTPEsiErrorRateLimit:
                    reset = e.headers.get("X-RateLimit-Reset", None)
                    if reset:
                        reset = int(reset)
                        self.cache.set("esi_rate_limit_reset", reset, ex=reset)
                    raise EsiErrorLimitException(reset=reset) from e
                raise HTTPClientError(status_code=e.status_code, headers=e.headers, data=e.data) from e

            if response.status_code == 304:
                raise HTTPNotModified(status_code=response.status_code, headers=response.headers)  # type: ignore

        return (data, response) if return_response else data

    def results(
        self, return_response: bool = False, force_refresh: bool = False, **extra
    ) -> tuple[list[Any], Response | Any | None] | list[Any]:
        all_results: list[Any] = []
        last_response: Response | None = None

        if self._has_page_param():
            current_page = 1
            total_pages = 1
            while current_page <= total_pages:
                self._kwargs["page"] = current_page
                data, response = self.result(return_response=True, force_refresh=force_refresh, **extra)
                last_response = response
                all_results.extend(data if isinstance(data, list) else [data])
                total_pages = int(response.headers.get("X-Pages", 1))
                logger.debug(f"ESI Page Fetched {self.url} - {current_page}/{total_pages}")
                current_page += 1
        elif self._has_cursor_param():
            # Untested, there are no cursor based endpoints in ESI
            params = self._kwargs.copy()
            params.update(extra)
            for cursor_param in ("after", "before"):
                if params.get(cursor_param):
                    break
            else:
                cursor_param = "after"
            while True:
                data, response = self.result(return_response=True, force_refresh=force_refresh, **params)
                last_response = response
                if not data:
                    break
                all_results.extend(data if isinstance(data, list) else [data])
                cursor_token = {k.lower(): v for k, v in response.headers.items()}.get(cursor_param)
                if not cursor_token:
                    break
                params[cursor_param] = cursor_token

        else:
            data, response = self.result(return_response=True, force_refresh=force_refresh, **extra)
            all_results.extend(data if isinstance(data, list) else [data])
            last_response = response

        return (all_results, last_response) if return_response else all_results
