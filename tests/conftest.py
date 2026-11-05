import os
import shutil
import tempfile
import pytest
from config import TestingConfig
from storage.json_storage import JSONStorage

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary sandbox directory for test JSON storage."""
    temp_dir = tempfile.mkdtemp(prefix="sharemeal_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def test_storage(test_data_dir):
    """Provide an isolated JSONStorage instance for tests."""
    return JSONStorage(data_dir=test_data_dir)
