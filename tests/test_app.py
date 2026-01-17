"""
Tests for the Mergington High School API
"""

import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
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
        "Math Olympiad": {
            "description": "Prepare for and compete in mathematics competitions.",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Science Club": {
            "description": "Explore science topics and conduct experiments.",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches.",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": []
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play in tournaments.",
            "schedule": "Fridays, 5:00 PM - 6:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create artwork.",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Drama Society": {
            "description": "Participate in acting, directing, and stage production.",
            "schedule": "Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test that activities can be retrieved successfully"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9  # Total number of activities
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that activity objects contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants(self, client):
        """Test that participants are returned correctly"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Math Olympiad should have no participants
        assert len(data["Math Olympiad"]["participants"]) == 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Math%20Olympiad/signup",
            params={"email": "new.student@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "new.student@mergington.edu" in data["message"]
        assert "Math Olympiad" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "new.student@mergington.edu" in activities_data["Math Olympiad"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test multiple students can sign up for the same activity"""
        response1 = client.post(
            "/activities/Science%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Science%20Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both students are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "student1@mergington.edu" in activities_data["Science Club"]["participants"]
        assert "student2@mergington.edu" in activities_data["Science Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        assert len(activities_data["Chess Club"]["participants"]) == 1
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_registered(self, client):
        """Test unregister for a student not registered for the activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_multiple_times(self, client):
        """Test that unregistering twice fails"""
        # First unregister should succeed
        response1 = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows"""
    
    def test_signup_then_unregister(self, client):
        """Test complete signup and unregister flow"""
        email = "integration.test@mergington.edu"
        activity = "Science Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]
    
    def test_signup_unregister_signup_again(self, client):
        """Test signup after unregistering from same activity"""
        email = "test.student@mergington.edu"
        activity = "Math Olympiad"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Second signup should succeed
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
