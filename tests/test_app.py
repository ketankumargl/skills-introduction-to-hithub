import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert expected_activity_name in response.json()
    assert response.json()[expected_activity_name]["max_participants"] == 12


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    params = {"email": email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    params = {"email": email}

    client.post(f"/activities/{activity_name}/signup", params=params)

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_missing_activity_returns_404():
    # Arrange
    activity_name = "Field Trip"
    params = {"email": "student@mergington.edu"}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_successfully_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    params = {"email": email}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"
    params = {"email": email}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
