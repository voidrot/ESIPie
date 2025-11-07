from types import SimpleNamespace

import pytest

from esipie import helpers

# Tests for helpers._build_user_agent
# - monkeypatch CONFIG in the helpers module to isolate from external config
# - cover cases with and without user_agent_url and missing attributes


def test_build_user_agent_includes_url_when_provided(monkeypatch):
    # Arrange: provide a CONFIG object with all expected attributes, including user_agent_url
    config = SimpleNamespace(
        user_agent_app_name="AppName",
        user_agent_app_version="1.2.3",
        user_agent_contact_email="me@example.com",
        user_agent_url="https://example.com",
        user_agent_lib_name="ProjectTitle",
        user_agent_lib_version="0.1.0",
        user_agent_lib_url="https://project.example.com",
    )
    monkeypatch.setattr(helpers, "CONFIG", config)

    # Act
    ua = helpers._build_user_agent()

    # Assert: url should be included with the "+<url>" prefix inside the parentheses
    expected = "AppName/1.2.3 (me@example.com; +https://example.com) ProjectTitle/0.1.0 (+https://project.example.com)"
    assert ua == expected


def test_build_user_agent_omits_url_when_missing_or_empty(monkeypatch):
    # Arrange: provide CONFIG where user_agent_url is falsy (None / empty string)
    for falsy_url in (None, ""):
        config = SimpleNamespace(
            user_agent_app_name="AppName",
            user_agent_app_version="1.2.3",
            user_agent_contact_email="me@example.com",
            user_agent_url=falsy_url,
            user_agent_lib_name="ProjectTitle",
            user_agent_lib_version="0.1.0",
            user_agent_lib_url="https://project.example.com",
        )
        monkeypatch.setattr(helpers, "CONFIG", config)

        # Act
        ua = helpers._build_user_agent()

        # Assert: parentheses should contain only the contact email when url is falsy
        expected = "AppName/1.2.3 (me@example.com) ProjectTitle/0.1.0 (+https://project.example.com)"
        assert ua == expected


def test_build_user_agent_raises_if_required_attribute_missing(monkeypatch):
    # Arrange: omit a required attribute to ensure AttributeError is raised
    config = SimpleNamespace(
        user_agent_app_name="AppName",
        # user_agent_app_version is intentionally missing
        user_agent_contact_email="me@example.com",
        user_agent_url=None,
        user_agent_lib_name="ProjectTitle",
        user_agent_lib_version="0.1.0",
        user_agent_lib_url="https://project.example.com",
    )
    monkeypatch.setattr(helpers, "CONFIG", config)

    # Act / Assert: attempting to build should raise AttributeError for missing attribute
    with pytest.raises(AttributeError):
        helpers._build_user_agent()


# Tests for helpers.get_esi_spec_url
# - monkeypatch CONFIG in the helpers module to isolate from external config
# - cover normal concatenation, behavior when base URL already has query params,
#   and missing-attribute error behavior.
def test_get_esi_spec_url_appends_compatibility_date(monkeypatch):
    # Arrange: CONFIG provides a simple base URL and a compatibility date
    config = SimpleNamespace(
        esi_spec_url="https://esi.example.com/openapi.json",
        esi_compatibility_date="2023-01-01",
    )
    monkeypatch.setattr(helpers, "CONFIG", config)

    # Act
    url = helpers.get_esi_spec_url()

    # Assert: exact concatenation with ?compatibility_date=...
    assert url == "https://esi.example.com/openapi.json?compatibility_date=2023-01-01"


def test_get_esi_spec_url_with_existing_query_params(monkeypatch):
    # Arrange: base URL already includes query parameters. Per function docstring,
    # the function performs simple concatenation and does not normalize existing queries.
    base = "https://esi.example.com/openapi.json?foo=bar"
    config = SimpleNamespace(
        esi_spec_url=base,
        esi_compatibility_date="2024-02-02",
    )
    monkeypatch.setattr(helpers, "CONFIG", config)

    # Act
    url = helpers.get_esi_spec_url()

    # Assert: function will naively append another ?compatibility_date=... (no encoding/merging)
    assert url == "https://esi.example.com/openapi.json?foo=bar?compatibility_date=2024-02-02"


def test_get_esi_spec_url_raises_if_required_attribute_missing(monkeypatch):
    # Arrange: omit esi_compatibility_date to ensure AttributeError is raised
    config = SimpleNamespace(
        esi_spec_url="https://esi.example.com/openapi.json",
        # esi_compatibility_date intentionally missing
    )
    monkeypatch.setattr(helpers, "CONFIG", config)

    # Act / Assert: attempting to build should raise AttributeError for missing attribute
    with pytest.raises(AttributeError):
        helpers.get_esi_spec_url()
