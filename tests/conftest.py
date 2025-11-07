import os


def pytest_configure(config):
    """Set required environment variables for tests."""
    os.environ.setdefault("USER_AGENT_CONTACT_EMAIL", "test@example.com")
    os.environ.setdefault("USER_AGENT_APP_NAME", "TestApp")
    os.environ.setdefault("USER_AGENT_APP_VERSION", "1.0.0")
