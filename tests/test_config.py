import pytest
from pydantic import ValidationError

from esipie.config import APIConfig, AuthConfig, CacheConfig, Config, UAConfig


class TestUAConfig:
    def test_default_values(self):
        """Test that UA config uses default values when no env vars are set."""
        with pytest.raises(ValidationError):
            UAConfig()

    def test_env_vars_loaded(self, monkeypatch):
        """Test that UA config loads values from environment variables."""
        monkeypatch.setenv("ESIPIE_UA_APP_NAME", "TestApp")
        monkeypatch.setenv("ESIPIE_UA_APP_VERSION", "1.0.0")
        monkeypatch.setenv("ESIPIE_UA_CONTACT_EMAIL", "test@example.com")

        config = UAConfig()
        assert config.app_name == "TestApp"
        assert config.app_version == "1.0.0"
        assert config.contact_email == "test@example.com"

    def test_partial_env_vars(self, monkeypatch):
        """Test that config fails when required env vars are missing."""
        monkeypatch.setenv("ESIPIE_UA_APP_NAME", "TestApp")
        # Missing app_version and contact_email

        with pytest.raises(ValidationError):
            UAConfig()


class TestAPIConfig:
    def test_default_values(self):
        """Test that API config uses default values."""
        config = APIConfig()
        assert config.base_url == "https://esi.evetech.net"
        assert config.timeout_seconds == 10
        assert config.compatibility_date == "2025-09-26"

    def test_env_vars_override_defaults(self, monkeypatch):
        """Test that environment variables override default values."""
        monkeypatch.setenv("ESIPIE_BASE_URL", "https://custom.esi.net")
        monkeypatch.setenv("ESIPIE_TIMEOUT_SECONDS", "30")
        monkeypatch.setenv("ESIPIE_COMPATIBILITY_DATE", "2025-10-01")

        config = APIConfig()
        assert config.base_url == "https://custom.esi.net"
        assert config.timeout_seconds == 30
        assert config.compatibility_date == "2025-10-01"

    def test_partial_env_vars(self, monkeypatch):
        """Test that only specified env vars override defaults."""
        monkeypatch.setenv("ESIPIE_TIMEOUT_SECONDS", "20")

        config = APIConfig()
        assert config.base_url == "https://esi.evetech.net"  # default
        assert config.timeout_seconds == 20  # overridden
        assert config.compatibility_date == "2025-09-26"  # default


class TestAuthConfig:
    def test_default_values(self, monkeypatch):
        """Test that auth config uses default values where available."""
        # Ensure required env vars are not set
        monkeypatch.delenv("ESIPIE_SSO_CLIENT_ID", raising=False)
        monkeypatch.delenv("ESIPIE_SSO_CLIENT_SECRET", raising=False)

        with pytest.raises(ValidationError):
            AuthConfig()

    def test_env_vars_loaded(self, monkeypatch):
        """Test that auth config loads values from environment variables."""
        monkeypatch.setenv("ESIPIE_SSO_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("ESIPIE_SSO_CLIENT_SECRET", "test_client_secret")
        monkeypatch.setenv("ESIPIE_OPENAPI_URL", "https://custom.openapi.json")
        monkeypatch.setenv("ESIPIE_CLIENT_TENANT", "singularity")

        config = AuthConfig()
        assert config.sso_client_id == "test_client_id"
        assert config.sso_client_secret == "test_client_secret"
        assert config.openapi_url == "https://custom.openapi.json"
        assert config.client_tenant == "singularity"


class TestCacheConfig:
    def test_default_values(self):
        """Test that cache config uses default values."""
        config = CacheConfig()
        assert config.redis_url == "redis://localhost:6379/0"
        assert config.spec_cache_duration == 3600
        assert config.disable_cache is False
        assert config.cache_prefix == "esipie"

    def test_env_vars_override_defaults(self, monkeypatch):
        """Test that environment variables override default values."""
        monkeypatch.setenv("ESIPIE_REDIS_URL", "redis://remote:6379/1")
        monkeypatch.setenv("ESIPIE_SPEC_CACHE_DURATION", "7200")
        monkeypatch.setenv("ESIPIE_DISABLE_CACHE", "true")
        monkeypatch.setenv("ESIPIE_CACHE_PREFIX", "custom_prefix")

        config = CacheConfig()
        assert config.redis_url == "redis://remote:6379/1"
        assert config.spec_cache_duration == 7200
        assert config.disable_cache is True
        assert config.cache_prefix == "custom_prefix"

    def test_boolean_env_var_parsing(self, monkeypatch):
        """Test that boolean environment variables are parsed correctly."""
        monkeypatch.setenv("ESIPIE_DISABLE_CACHE", "false")
        config = CacheConfig()
        assert config.disable_cache is False

        monkeypatch.setenv("ESIPIE_DISABLE_CACHE", "true")
        config = CacheConfig()
        assert config.disable_cache is True


class TestMainConfig:
    def test_config_composition(self, monkeypatch):
        """Test that the main Config class properly composes sub-configs."""
        # Set required env vars for UA config
        monkeypatch.setenv("ESIPIE_UA_APP_NAME", "TestApp")
        monkeypatch.setenv("ESIPIE_UA_APP_VERSION", "1.0.0")
        monkeypatch.setenv("ESIPIE_UA_CONTACT_EMAIL", "test@example.com")

        # Set some overrides for other configs
        monkeypatch.setenv("ESIPIE_BASE_URL", "https://test.esi.net")
        monkeypatch.setenv("ESIPIE_SSO_CLIENT_ID", "test_id")
        monkeypatch.setenv("ESIPIE_SSO_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("ESIPIE_DISABLE_CACHE", "true")

        config = Config()

        # Test UA config
        assert config.ua.app_name == "TestApp"
        assert config.ua.app_version == "1.0.0"
        assert config.ua.contact_email == "test@example.com"

        # Test API config (with override)
        assert config.api.base_url == "https://test.esi.net"
        assert config.api.timeout_seconds == 10  # default

        # Test auth config
        assert config.auth.sso_client_id == "test_id"
        assert config.auth.sso_client_secret == "test_secret"
        assert config.auth.client_tenant == "tranquility"  # default

        # Test cache config (with override)
        assert config.cache.disable_cache is True
        assert config.cache.redis_url == "redis://localhost:6379/0"  # default

    def test_config_without_required_env_vars_fails(self):
        """Test that Config fails when required environment variables are missing."""
        with pytest.raises(ValidationError):
            Config()
