# Standard Library
import os

# Third Party
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables from .env file before tests run."""
    load_dotenv()


@pytest.fixture(scope="session")
def readwise_api_key():
    """Fixture to provide the Readwise API key, skipping tests if not set."""
    api_key = os.getenv("READWISE_API_KEY")
    if not api_key:
        pytest.skip("READWISE_API_KEY environment variable not set, skipping integration test.")
    return api_key
