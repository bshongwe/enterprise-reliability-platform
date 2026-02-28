import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    os.environ['API_KEY'] = 'test-key'
    os.environ['API_KEY_HASH'] = ''
