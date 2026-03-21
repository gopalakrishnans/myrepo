def test_list_hospitals(client):
    resp = client.get("/api/v1/hospitals")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


def test_search_hospitals(client):
    resp = client.get("/api/v1/hospitals?q=Test")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_filter_hospitals_by_state(client):
    resp = client.get("/api/v1/hospitals?state=NY")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["state"] == "NY"


def test_get_hospital(client):
    resp = client.get("/api/v1/hospitals/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Hospital A"


def test_get_hospital_not_found(client):
    resp = client.get("/api/v1/hospitals/999")
    assert resp.status_code == 404


def test_health_check(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
