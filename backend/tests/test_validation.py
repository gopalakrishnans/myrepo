"""Tests for API input validation and error handling."""


def test_prices_missing_procedure_id(client):
    resp = client.get("/api/v1/prices")
    assert resp.status_code == 422


def test_prices_invalid_sort_by(client):
    resp = client.get("/api/v1/prices?procedure_id=1&sort_by=invalid")
    assert resp.status_code == 422


def test_prices_limit_too_large(client):
    resp = client.get("/api/v1/prices?procedure_id=1&limit=999")
    assert resp.status_code == 422


def test_prices_negative_offset(client):
    resp = client.get("/api/v1/prices?procedure_id=1&offset=-1")
    assert resp.status_code == 422


def test_prices_nonexistent_procedure(client):
    resp = client.get("/api/v1/prices?procedure_id=9999")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_compare_too_many_hospitals(client):
    resp = client.get("/api/v1/prices/compare?procedure_id=1&hospital_ids=1,2,3,4,5")
    assert resp.status_code == 400


def test_compare_missing_procedure_id(client):
    resp = client.get("/api/v1/prices/compare?hospital_ids=1,2")
    assert resp.status_code == 422


def test_compare_missing_hospital_ids(client):
    resp = client.get("/api/v1/prices/compare?procedure_id=1")
    assert resp.status_code == 422


def test_compare_invalid_hospital_ids(client):
    resp = client.get("/api/v1/prices/compare?procedure_id=1&hospital_ids=abc,def")
    assert resp.status_code == 400


def test_compare_nonexistent_procedure(client):
    resp = client.get("/api/v1/prices/compare?procedure_id=9999&hospital_ids=1,2")
    assert resp.status_code == 404


def test_hospitals_nearby_short_zip(client):
    resp = client.get("/api/v1/hospitals/nearby?zip_code=123")
    assert resp.status_code == 422


def test_hospitals_nearby_long_zip(client):
    resp = client.get("/api/v1/hospitals/nearby?zip_code=1234567")
    assert resp.status_code == 422


def test_hospitals_nearby_non_digit_zip(client):
    resp = client.get("/api/v1/hospitals/nearby?zip_code=abcde")
    assert resp.status_code == 400
    assert "digits" in resp.json()["detail"].lower()


def test_hospitals_nearby_missing_zip(client):
    resp = client.get("/api/v1/hospitals/nearby")
    assert resp.status_code == 422


def test_hospitals_limit_too_large(client):
    resp = client.get("/api/v1/hospitals?limit=999")
    assert resp.status_code == 422


def test_hospitals_negative_offset(client):
    resp = client.get("/api/v1/hospitals?offset=-5")
    assert resp.status_code == 422


def test_procedures_search_limit_too_large(client):
    resp = client.get("/api/v1/procedures/search?limit=999")
    assert resp.status_code == 422


def test_procedures_search_empty_query(client):
    resp = client.get("/api/v1/procedures/search")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_procedures_search_no_results(client):
    resp = client.get("/api/v1/procedures/search?q=zzzznonexistent")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_stats_nonexistent_procedure(client):
    resp = client.get("/api/v1/stats/procedure/9999")
    assert resp.status_code == 404


def test_stats_state_filter(client):
    resp = client.get("/api/v1/stats/procedure/1?state=NY")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cash_price_count"] >= 1


def test_hospital_id_string(client):
    resp = client.get("/api/v1/hospitals/abc")
    assert resp.status_code == 422


def test_procedure_id_string(client):
    resp = client.get("/api/v1/procedures/abc")
    assert resp.status_code == 422


def test_prices_state_filter_uppercase(client):
    resp = client.get("/api/v1/prices?procedure_id=1&state=ny")
    assert resp.status_code == 200
