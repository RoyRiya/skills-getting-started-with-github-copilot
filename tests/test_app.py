import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_all_activities():
    # Arrange
    with TestClient(app) as client:
        # Act
        response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Soccer Club"
    email = "charlie@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    email = "test@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            "/activities/Unknown/signup",
            params={"email": email}
        )

    # Assert
    assert response.status_code == 404


def test_signup_for_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_unregisters_student():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "nonexistent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
