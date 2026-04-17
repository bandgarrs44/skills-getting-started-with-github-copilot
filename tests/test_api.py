"""Integration tests for Mergington High School Activities API using AAA pattern."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all(self, client):
        """
        Arrange: Use default activities fixture
        Act: GET /activities
        Assert: Status 200, response contains all activities with correct structure
        """
        # Arrange: fixture provides client with fresh activities

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert activities["Chess Club"]["max_participants"] == 12
        assert "participants" in activities["Chess Club"]
        assert isinstance(activities["Chess Club"]["participants"], list)


class TestRootRedirect:
    """Tests for GET / root endpoint."""

    def test_root_redirect(self, client):
        """
        Arrange: No setup needed
        Act: GET / with allow_redirects=False
        Assert: Status 307, Location header points to /static/index.html
        """
        # Arrange: fixture provides client

        # Act
        response = client.get("/", allow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupSuccess:
    """Tests for successful signup scenarios."""

    def test_signup_new_student(self, client):
        """
        Arrange: Fresh activities, new email "newstudent@mergington.edu"
        Act: POST /activities/Chess Club/signup?email=newstudent@mergington.edu
        Assert: Status 200, response message confirms signup
        """
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {new_email} for {activity_name}"

    def test_participant_added_to_list(self, client):
        """
        Arrange: Fresh activities, new email
        Act: POST signup, then GET /activities
        Assert: Chess Club's participants list includes the new email
        """
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act: Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        assert signup_response.status_code == 200

        # Act: Get activities
        get_response = client.get("/activities")

        # Assert
        assert get_response.status_code == 200
        activities = get_response.json()
        assert new_email in activities[activity_name]["participants"]


class TestSignupErrors:
    """Tests for signup error scenarios."""

    def test_signup_nonexistent_activity(self, client):
        """
        Arrange: Fresh activities, invalid activity name
        Act: POST /activities/Fake Activity/signup?email=test@mergington.edu
        Assert: Status 404, detail contains "Activity not found"
        """
        # Arrange
        invalid_activity = "Fake Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self, client):
        """
        Arrange: Fresh activities, email already in Chess Club (michael@mergington.edu)
        Act: POST signup for existing participant
        Assert: Status 400, detail contains "already signed up"
        """
        # Arrange
        existing_email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]


class TestRemoveParticipantSuccess:
    """Tests for successful participant removal scenarios."""

    def test_remove_participant_success(self, client):
        """
        Arrange: Fresh activities, target michael@mergington.edu in Chess Club
        Act: DELETE /activities/Chess Club/participants/michael@mergington.edu
        Assert: Status 200, response message confirms removal
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity_name}"

    def test_participant_removed_from_list(self, client):
        """
        Arrange: Fresh activities, existing participant
        Act: DELETE participant, then GET /activities
        Assert: Participant no longer in Chess Club's participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Remove
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert delete_response.status_code == 200

        # Act: Get activities
        get_response = client.get("/activities")

        # Assert
        assert get_response.status_code == 200
        activities = get_response.json()
        assert email not in activities[activity_name]["participants"]


class TestRemoveParticipantErrors:
    """Tests for participant removal error scenarios."""

    def test_remove_nonexistent_participant(self, client):
        """
        Arrange: Fresh activities, email not in Chess Club
        Act: DELETE /activities/Chess Club/participants/notinclub@mergington.edu
        Assert: Status 404, detail contains "Participant not found"
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notinclub@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_from_nonexistent_activity(self, client):
        """
        Arrange: Fresh activities
        Act: DELETE /activities/Fake Activity/participants/someone@mergington.edu
        Assert: Status 404, detail contains "Activity not found"
        """
        # Arrange
        invalid_activity = "Fake Activity"
        email = "someone@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
