import os
import sys
from fastapi.testclient import TestClient

# Ensure the `src` directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import app as tested_app

client = TestClient(tested_app.app)


def test_root_redirect():
    resp = client.get("/", allow_redirects=False)
    assert resp.status_code in (307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure a clean state for the test email
    participants = tested_app.activities[activity]["participants"]
    if email in participants:
        participants.remove(email)

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in tested_app.activities[activity]["participants"]

    # Duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400

    # Unregister
    r3 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r3.status_code == 200
    assert email not in tested_app.activities[activity]["participants"]

    # Unregistering again should return 404
    r4 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r4.status_code == 404


def test_activity_not_found():
    r = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert r.status_code == 404
    r2 = client.delete("/activities/Nonexistent/participants", params={"email": "a@b.com"})
    assert r2.status_code == 404
