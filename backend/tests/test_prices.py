def test_get_prices(client):
    resp = client.get("/api/v1/prices?procedure_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


def test_get_prices_filter_state(client):
    resp = client.get("/api/v1/prices?procedure_id=1&state=NY")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["hospital_state"] == "NY"


def test_compare_prices(client):
    resp = client.get("/api/v1/prices/compare?procedure_id=1&hospital_ids=1,2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["procedure_name"] == "Brain MRI with Contrast"
    assert len(data["hospitals"]) == 2


def test_compare_too_few_hospitals(client):
    resp = client.get("/api/v1/prices/compare?procedure_id=1&hospital_ids=1")
    assert resp.status_code == 400


def test_procedure_stats(client):
    resp = client.get("/api/v1/stats/procedure/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plain_language_name"] == "Brain MRI with Contrast"
    assert data["fair_price"] is not None
    assert data["cash_price_count"] >= 1


def test_procedure_stats_not_found(client):
    resp = client.get("/api/v1/stats/procedure/999")
    assert resp.status_code == 404
