"""
Verification of Flask routes and static assets.
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
import json

client = app.test_client()

def test_routes():
    # 1. Landing page at /
    r = client.get('/')
    print(f"GET / -> {r.status_code}")
    assert r.status_code == 200
    assert b"SSPU Campus Navigator" in r.data
    assert b"Open Navigator" in r.data

    # 2. Secret pathways assets
    r = client.get('/secret-pathways-assets/three.min.js')
    print(f"GET /secret-pathways-assets/three.min.js -> {r.status_code} ({len(r.data)} bytes)")
    assert r.status_code == 200
    assert len(r.data) > 100000

    r = client.get('/secret-pathways-assets/fonts.css')
    print(f"GET /secret-pathways-assets/fonts.css -> {r.status_code}")
    assert r.status_code == 200

    r = client.get('/secret-pathways-assets/foreground/png/temple-wall.webp')
    print(f"GET temple-wall.webp -> {r.status_code} ({len(r.data)} bytes)")
    assert r.status_code == 200

    # 3. Navigator app
    r = client.get('/app')
    print(f"GET /app -> {r.status_code}")
    assert r.status_code == 200
    assert b"CAMPUS NAVIGATOR" in r.data
    assert b"campus-svg-map" in r.data

    # 4. Admin login page
    r = client.get('/admin/login')
    print(f"GET /admin/login -> {r.status_code}")
    assert r.status_code == 200
    assert b"Admin@123" in r.data

    # 5. Admin dashboard redirect when not logged in
    r = client.get('/admin')
    print(f"GET /admin (unauthed) -> {r.status_code} (redirects to {r.headers.get('Location')})")
    assert r.status_code in [302, 301]

    # 6. API Facilities
    r = client.get('/api/facilities')
    print(f"GET /api/facilities -> {r.status_code}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["count"] >= 30
    print(f"  Total facilities returned: {data['count']}")

    # 7. API Search & Filter
    r = client.get('/api/facilities?q=lab')
    data = r.get_json()
    print(f"GET /api/facilities?q=lab -> count {data['count']}")
    assert data['count'] > 0

    r = client.get('/api/facilities?category=Library')
    data = r.get_json()
    print(f"GET /api/facilities?category=Library -> count {data['count']}")
    assert data['count'] >= 2

    # 8. API Route
    r = client.get('/api/route?from=1&to=8')
    print(f"GET /api/route?from=1&to=8 -> {r.status_code}")
    assert r.status_code == 200
    route = r.get_json()
    assert route["success"] is True
    print(f"  Route 1 -> 8: {route['total_distance']}m, {route['walking_time_formatted']}, steps: {len(route['steps'])}")

    # 9. API Auth & CRUD
    login_res = client.post('/api/login', json={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    print("Admin login -> 200 OK")

    # Authed Admin dashboard
    r = client.get('/admin')
    assert r.status_code == 200
    print("GET /admin (authed) -> 200 OK")

    # Create facility
    new_fac = {
        "name": "Robotics & Drone Testing Range",
        "category": "Laboratory",
        "building": "Mechanical & Workshops Block (C)",
        "floor": "Ground Floor",
        "operating_hours": "Mon-Sat 08:30-17:00",
        "description": "Outdoor tethered drone test enclosure and autonomous ground vehicle test track.",
        "contact": "+91 20 6793 5078",
        "node_id": "N_WORKSHOP_ENTRANCE",
        "x": 890,
        "y": 280
    }
    create_res = client.post('/api/facilities', json=new_fac)
    print(f"POST /api/facilities -> {create_res.status_code}")
    assert create_res.status_code == 201
    created_id = create_res.get_json()["facility"]["id"]

    # Verify created appears immediately
    fac_res = client.get(f'/api/facilities/{created_id}')
    assert fac_res.status_code == 200
    assert fac_res.get_json()["facility"]["name"] == new_fac["name"]
    print(f"Facility #{created_id} verified on API!")

    # Delete facility
    del_res = client.delete(f'/api/facilities/{created_id}')
    assert del_res.status_code == 200
    print("Facility deleted cleanly.")

    print("\nALL INTEGRATION CHECKS PASSED!")

if __name__ == "__main__":
    test_routes()
