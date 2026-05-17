"""Tests for all Space Data SOA Platform microservices"""
import requests
import pytest
import time

BASE = {
    "satellite": "http://localhost:8080",
    "weather": "http://localhost:8001",
    "astro": "http://localhost:8002",
    "missions": "http://localhost:8003",
    "users": "http://localhost:8004",
}


# ===== Health checks =====
class TestHealthChecks:
    def test_satellite_tracker_health(self):
        r = requests.get(f"{BASE['satellite']}/")
        assert r.status_code == 200
        assert r.json()["status"] == "online"

    def test_space_weather_health(self):
        r = requests.get(f"{BASE['weather']}/")
        assert r.status_code == 200

    def test_astro_objects_health(self):
        r = requests.get(f"{BASE['astro']}/")
        assert r.status_code == 200
        assert r.json()["status"] == "online"

    def test_mission_data_health(self):
        r = requests.get(f"{BASE['missions']}/")
        assert r.status_code == 200

    def test_user_service_health(self):
        r = requests.get(f"{BASE['users']}/")
        assert r.status_code == 200


# ===== User Service =====
class TestUserService:
    unique = str(int(time.time()))

    def test_register(self):
        r = requests.post(f"{BASE['users']}/register", json={
            "username": f"testuser_{self.unique}",
            "email": f"test_{self.unique}@space.com",
            "password": "testpass123"
        })
        assert r.status_code == 200
        assert r.json()["username"] == f"testuser_{self.unique}"

    def test_register_duplicate(self):
        r = requests.post(f"{BASE['users']}/register", json={
            "username": f"testuser_{self.unique}",
            "email": f"test_{self.unique}@space.com",
            "password": "testpass123"
        })
        assert r.status_code == 400

    def test_login(self):
        r = requests.post(f"{BASE['users']}/login", json={
            "username": f"testuser_{self.unique}",
            "password": "testpass123"
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        r = requests.post(f"{BASE['users']}/login", json={
            "username": f"testuser_{self.unique}",
            "password": "wrongpass"
        })
        assert r.status_code == 401

    def test_get_profile(self):
        login = requests.post(f"{BASE['users']}/login", json={
            "username": f"testuser_{self.unique}", "password": "testpass123"
        })
        token = login.json()["access_token"]
        r = requests.get(f"{BASE['users']}/users/me",
                         headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["username"] == f"testuser_{self.unique}"


# ===== Satellite Tracker =====
class TestSatelliteTracker:
    def test_fetch_tle(self):
        r = requests.get(f"{BASE['satellite']}/fetch-tle")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ["success", "error"]

    def test_get_satellites(self):
        r = requests.get(f"{BASE['satellite']}/satellites")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_add_test_satellite(self):
        r = requests.get(f"{BASE['satellite']}/add-test")
        assert r.status_code == 200


# ===== Space Weather =====
class TestSpaceWeather:
    def test_kp_index(self):
        r = requests.get(f"{BASE['weather']}/noaa-kp-index")
        assert r.status_code == 200
        assert r.json()["status"] == "success"

    def test_kp_history(self):
        r = requests.get(f"{BASE['weather']}/kp-history")
        assert r.status_code == 200
        assert "data" in r.json()

    def test_donki_cme(self):
        r = requests.get(f"{BASE['weather']}/donki/cme")
        assert r.status_code == 200
        assert "data" in r.json()

    def test_donki_flr(self):
        r = requests.get(f"{BASE['weather']}/donki/flr")
        assert r.status_code == 200
        assert "data" in r.json()

    def test_donki_gst(self):
        r = requests.get(f"{BASE['weather']}/donki/gst")
        assert r.status_code == 200
        assert "data" in r.json()


# ===== Astro Objects (requires auth for write) =====
class TestAstroObjects:
    def _get_token(self):
        unique = str(int(time.time()))
        requests.post(f"{BASE['users']}/register", json={
            "username": f"astro_{unique}", "email": f"astro_{unique}@test.com", "password": "pass123"
        })
        r = requests.post(f"{BASE['users']}/login", json={
            "username": f"astro_{unique}", "password": "pass123"
        })
        return r.json()["access_token"]

    def test_get_objects(self):
        r = requests.get(f"{BASE['astro']}/objects/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_requires_auth(self):
        r = requests.post(f"{BASE['astro']}/objects/", json={
            "name": "Test Star", "object_type": "star",
            "right_ascension": "05h 34m", "declination": "+22 00"
        })
        assert r.status_code == 401

    def test_create_with_auth(self):
        token = self._get_token()
        r = requests.post(f"{BASE['astro']}/objects/", json={
            "name": "Betelgeuse", "object_type": "star",
            "right_ascension": "05h 55m", "declination": "+07 24",
            "distance_ly": 642.5
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["name"] == "Betelgeuse"


# ===== Mission Data (requires auth for write) =====
class TestMissionData:
    def _get_token(self):
        unique = str(int(time.time()))
        requests.post(f"{BASE['users']}/register", json={
            "username": f"mission_{unique}", "email": f"mission_{unique}@test.com", "password": "pass123"
        })
        r = requests.post(f"{BASE['users']}/login", json={
            "username": f"mission_{unique}", "password": "pass123"
        })
        return r.json()["access_token"]

    def test_get_missions(self):
        r = requests.get(f"{BASE['missions']}/missions/")
        assert r.status_code == 200

    def test_apod(self):
        r = requests.get(f"{BASE['missions']}/apod/")
        assert r.status_code == 200

    def test_neo(self):
        r = requests.get(f"{BASE['missions']}/neo/")
        assert r.status_code == 200

    def test_create_requires_auth(self):
        r = requests.post(f"{BASE['missions']}/missions/", json={
            "name": "Test", "agency": "NASA", "status": "planned"
        })
        assert r.status_code == 401

    def test_create_with_auth(self):
        token = self._get_token()
        r = requests.post(f"{BASE['missions']}/missions/", json={
            "name": "Artemis III", "agency": "NASA", "status": "planned",
            "description": "Moon landing mission"
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["name"] == "Artemis III"
