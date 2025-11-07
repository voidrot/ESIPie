from tenacity import AsyncRetrying, Retrying, retry_if_exception, stop_after_attempt, wait_combine, wait_exponential

from esipie.config import CONFIG
from esipie.exceptions import EsiErrorLimitException


def _build_user_agent() -> str:
    """
    Construct a sanitized User-Agent string from the given configuration and package metadata.

    Returns
    -------
    str
        A User-Agent string composed of three parts separated by spaces:
        1) "<SanitizedAppName>/<app_version>"
        2) "(<contact_email>)" or "(<contact_email>; +<url>)" if a URL is provided
        3) "<SanitizedPackageTitle>/<package_version> (+<package_url>)"

        Application and package names are sanitized using pascal_case_string. Package
        metadata (title, version and url) are taken from the module-level globals
        __title__, __version__ and __url__.

    Examples
    --------
    # When config.user_agent_url is provided:
    "AppName/1.2.3 (me@example.com; +https://example.com) ProjectTitle/0.1.0 (+https://project.example.com)"

    # When config.user_agent_url is not provided:
    "AppName/1.2.3 (me@example.com) ProjectTitle/0.1.0 (+https://project.example.com)"

    Notes
    -----
    - This function does not perform I/O.
    - If the expected attributes are missing from config, AttributeError may be raised.
    """

    return (
        f"{CONFIG.user_agent_app_name}/{CONFIG.user_agent_app_version} "
        f"({CONFIG.user_agent_contact_email}{f'; +{CONFIG.user_agent_url})' if CONFIG.user_agent_url else ')'} "
        f"{CONFIG.user_agent_lib_name}/{CONFIG.user_agent_lib_version} (+{CONFIG.user_agent_lib_url})"
    )


def get_esi_spec_url() -> str:
    """
    Return the ESI specification URL with the compatibility date query parameter appended.

    Returns
    -------
    str
        The assembled URL in the form "<esi_spec_url>?compatibility_date=<esi_compatibility_date>".

    Notes
    -----
    This function performs a simple string concatenation to append the query parameter.
    It does not perform URL encoding or validation and does not handle cases where
    the base URL already includes existing query parameters.
    """
    base_url = CONFIG.esi_spec_url
    return f"{base_url}?compatibility_date={CONFIG.esi_compatibility_date}"


def _httpx_exceptions(exc: BaseException) -> bool:
    if isinstance(exc, EsiErrorLimitException):
        return False
    return True


def http_retry_sync() -> Retrying:
    return Retrying(
        retry=retry_if_exception(_httpx_exceptions),
        wait=wait_combine(
            wait_exponential(multiplier=1, min=1, max=10),
        ),
        stop=stop_after_attempt(3),
        reraise=True,
    )

