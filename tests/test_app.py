import pytest
from fastapi.testclient import TestClient
import src.app as app_module

# Copy of original activities data for resetting between tests
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball training and games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and participate in friendly matches",
        "schedule": "Saturdays, 10:00 AM - 12:00 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "lucy@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media techniques",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act in plays, develop stage presence, and explore theatrical arts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Compete in science competitions and conduct experiments",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation skills and compete in debate competitions",
        "schedule": "Mondays and Thursdays, 4:30 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "mason@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test to ensure isolation"""
    # Arrange: Reset to original state
    app_module.activities = ORIGINAL_ACTIVITIES.copy()
    yield
    # Cleanup: Reset again after test
    app_module.activities = ORIGINAL_ACTIVITIES.copy()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app_module.app)


def test_root_redirect(client):
    """Test that root endpoint redirects to static index"""
    # Arrange - client is set up

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test retrieving all activities"""
    # Arrange - activities are reset to original

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Number of activities
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == {"message": f"Signed up {email} for {activity_name}"}
    # Verify the participant was added
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == {"message": f"Unregistered {email} from {activity_name}"}
    # Verify the participant was removed
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister from non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_participant_not_found(client):
    """Test unregister when student is not signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"  # Not in participants

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"