"""
pytest for Harvey FastAPI
"""

import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harvey_api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "uptime_sec" in data
    assert "total_skills" in data


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Harvey" in r.text


def test_skills_endpoint(client):
    r = client.get("/skills")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_task_submit(client):
    task = {"task_type": "health", "payload": {}}
    r = client.post("/tasks/submit", json=task)
    assert r.status_code == 200
    data = r.json()
    assert "task_id" in data
    assert data["status"] in ("pending", "running", "done")


def test_task_get(client):
    # 先提交
    task = {"task_type": "health", "payload": {}}
    r = client.post("/tasks/submit", json=task)
    task_id = r.json()["task_id"]
    # 再查询
    r2 = client.get(f"/tasks/{task_id}")
    assert r2.status_code == 200
    assert r2.json()["task_id"] == task_id


def test_task_not_found(client):
    r = client.get("/tasks/nonexistent_task_xyz")
    assert r.status_code == 404


def test_skills_with_limit(client):
    r = client.get("/skills?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5
