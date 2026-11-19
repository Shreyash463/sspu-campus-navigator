"""
Pytest Test Suite for SSPU Campus Navigator
Covers:
- Facility CRUD
- Authentication requirement on write endpoints
- Search and combined filters
- Route correctness on known pairs & same-facility
- Graceful handling of invalid and non-existent routes
- Form & data validation errors
- Live open/closed operating hours logic
- Landing page served at '/' with 200 OK
- Asset serving at '/secret-pathways-assets/three.min.js'
- Localised asset URL resolution
"""

import os
import pytest
from datetime import datetime, time
from app import app
from database import init_db, check_is_open, get_facilities, get_facility
from graph import generate_route

@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        init_db(force_reseed=True)
    yield

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_landing_page_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"SSPU Campus Navigator" in res.data
    assert b"Open Navigator" in res.data

def test_threejs_asset_served(client):
    res = client.get("/secret-pathways-assets/three.min.js")
    assert res.status_code == 200
    assert len(res.data) > 100000

def test_fonts_and_images_served(client):
    res = client.get("/secret-pathways-assets/fonts.css")
    assert res.status_code == 200
    res_img = client.get("/secret-pathways-assets/foreground/png/temple-wall.webp")
    assert res_img.status_code == 200
    assert len(res_img.data) > 10000

def test_navigator_app_served(client):
    res = client.get("/app")
    assert res.status_code == 200
    assert b"CAMPUS NAVIGATOR" in res.data
    assert b"campus-svg-map" in res.data

def test_facilities_list_and_count(client):
    res = client.get("/api/facilities")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] >= 30
    assert len(data["facilities"]) >= 30

def test_facility_details_by_id(client):
    res = client.get("/api/facilities/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["facility"]["name"] == "Main Campus Gate & Security Post"
    assert data["facility"]["building"] == "Main Entrance & Plaza"
    assert "is_open" in data["facility"]

def test_facility_not_found(client):
    res = client.get("/api/facilities/99999")
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False

def test_facility_search_query(client):
    res = client.get("/api/facilities?q=Robotics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] >= 1
    assert any("Robotics" in f["name"] for f in data["facilities"])

def test_combined_filters(client):
    # Filter by category and building
    res = client.get("/api/facilities?category=Laboratory&building=Science+%26+Computing+Hub+(B)")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] >= 2
    for f in data["facilities"]:
        assert f["category"] == "Laboratory"
        assert f["building"] == "Science & Computing Hub (B)"

def test_auth_required_for_writes(client):
    # Attempt unauthenticated create
    new_data = {
        "name": "Unauthorized Lab",
        "category": "Laboratory",
        "building": "Engineering & Tech Block (A)",
        "floor": "1st Floor",
        "description": "Test",
        "operating_hours": "09:00-17:00",
        "x": 400, "y": 200
    }
    res = client.post("/api/facilities", json=new_data)
    assert res.status_code == 401

    # Attempt unauthenticated update
    res = client.put("/api/facilities/1", json=new_data)
    assert res.status_code == 401

    # Attempt unauthenticated delete
    res = client.delete("/api/facilities/1")
    assert res.status_code == 401

def test_facility_crud_lifecycle(client):
    # 1. Login as admin
    login_res = client.post("/api/login", json={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    assert login_res.get_json()["success"] is True

    # 2. Create facility
    fac_payload = {
        "name": "Mechatronics & Drone Testing Lab",
        "category": "Laboratory",
        "building": "Mechanical & Workshops Block (C)",
        "floor": "Ground Floor",
        "description": "State of the art precision drone test bench and autopilot testing.",
        "operating_hours": "Mon-Fri 08:30-18:00",
        "contact": "+91 20 6793 5079",
        "node_id": "N_WORKSHOP_ENTRANCE",
        "x": 880,
        "y": 240
    }
    create_res = client.post("/api/facilities", json=fac_payload)
    assert create_res.status_code == 201
    created = create_res.get_json()["facility"]
    new_id = created["id"]
    assert created["name"] == fac_payload["name"]

    # 3. Read back
    read_res = client.get(f"/api/facilities/{new_id}")
    assert read_res.status_code == 200
    assert read_res.get_json()["facility"]["name"] == fac_payload["name"]

    # 4. Update
    update_payload = dict(fac_payload)
    update_payload["name"] = "Advanced Mechatronics & Autonomous Drone Lab"
    update_res = client.put(f"/api/facilities/{new_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.get_json()["facility"]["name"] == update_payload["name"]

    # 5. Delete
    delete_res = client.delete(f"/api/facilities/{new_id}")
    assert delete_res.status_code == 200

    # 6. Verify deleted
    get_res = client.get(f"/api/facilities/{new_id}")
    assert get_res.status_code == 404

def test_validation_errors(client):
    # Login
    client.post("/api/login", json={"username": "admin", "password": "Admin@123"})

    # Missing required field 'name'
    bad_payload = {
        "category": "Laboratory",
        "building": "Main Academic",
        "floor": "Ground Floor",
        "description": "No name",
        "operating_hours": "09:00-17:00",
        "x": 100, "y": 100
    }
    res = client.post("/api/facilities", json=bad_payload)
    assert res.status_code == 400
    assert "Missing required fields" in res.get_json()["error"]

    # Out of bounds coordinates (x: 1500)
    out_of_bounds = {
        "name": "Invalid Coords Lab",
        "category": "Laboratory",
        "building": "Main Academic",
        "floor": "Ground Floor",
        "description": "Test",
        "operating_hours": "09:00-17:00",
        "x": 1500, "y": 100
    }
    res = client.post("/api/facilities", json=out_of_bounds)
    assert res.status_code == 400
    assert "out of bounds" in res.get_json()["error"]

def test_route_calculation_known_pair():
    # Route from Main Gate (ID 1) to Central Library (ID 8)
    route = generate_route(1, 8)
    assert route["success"] is True
    assert route["total_distance"] > 300
    assert route["walking_time_minutes"] > 3.0
    assert len(route["steps"]) >= 4
    assert len(route["coordinates"]) >= 4
    assert any("Central Library" in s for s in route["steps"])

def test_route_same_facility():
    # Route from ID 5 to ID 5
    route = generate_route(5, 5)
    assert route["success"] is True
    assert route["total_distance"] == 0.0
    assert route["is_same_facility"] is True
    assert "already at" in route["steps"][0]

def test_route_non_existent_facility():
    route = generate_route(1, 99999)
    assert route["success"] is False
    assert "not found" in route["error"].lower()

def test_open_closed_hours_logic():
    # 24 Hours
    is_open, badge = check_is_open("24 Hours")
    assert is_open is True
    assert "24 Hours" in badge

    # Tuesday 12:00 PM against Mon-Sat 09:00-17:00 -> Open
    tuesday_noon = datetime(2026, 11, 17, 12, 0, 0) # weekday = 1 (Tue)
    is_open, badge = check_is_open("Mon-Sat 09:00-17:00", tuesday_noon)
    assert is_open is True
    assert "Open now" in badge

    # Tuesday 20:00 PM against Mon-Sat 09:00-17:00 -> Closed
    tuesday_night = datetime(2026, 11, 17, 20, 0, 0)
    is_open, badge = check_is_open("Mon-Sat 09:00-17:00", tuesday_night)
    assert is_open is False
    assert "Closed" in badge

    # Sunday 12:00 PM against Mon-Fri 09:00-17:00 -> Closed today
    sunday_noon = datetime(2026, 11, 22, 12, 0, 0) # weekday = 6 (Sun)
    is_open, badge = check_is_open("Mon-Fri 09:00-17:00", sunday_noon)
    assert is_open is False
    assert "Closed today" in badge

def test_audit_logging(client):
    client.post("/api/login", json={"username": "admin", "password": "Admin@123"})
    res = client.get("/api/audit")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["logs"]) > 0
    assert any("ADMIN_LOGIN" in l["action"] for l in data["logs"])

def test_bonus_ask_campus(client):
    res = client.post("/api/ask", json={"question": "Where is the library and reading room?"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["matched_facility_ids"]) > 0
