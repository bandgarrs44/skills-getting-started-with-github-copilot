"""Pytest configuration and shared fixtures for API tests."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient with a fresh copy of activities for test isolation.
    Each test gets a clean activities dictionary to prevent test interdependencies.
    """
    # Deep copy activities to isolate each test
    original_activities = copy.deepcopy(activities)
    app.activities = copy.deepcopy(original_activities)
    
    # Patch the app's activities module-level variable
    import src.app
    src.app.activities = app.activities
    
    yield TestClient(app)
    
    # Restore original activities after test
    src.app.activities = original_activities
