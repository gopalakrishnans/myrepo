def test_search_procedures(client):
    resp = client.get("/api/v1/procedures/search?q=mri")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert "Brain MRI" in data["items"][0]["plain_language_name"]


def test_search_by_code(client):
    resp = client.get("/api/v1/procedures/search?q=70553")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_search_by_category(client):
    resp = client.get("/api/v1/procedures/search?category=Lab")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_get_categories(client):
    resp = client.get("/api/v1/procedures/categories")
    assert resp.status_code == 200
    cats = resp.json()
    assert "Imaging" in cats
    assert "Lab" in cats


def test_get_procedure(client):
    resp = client.get("/api/v1/procedures/1")
    assert resp.status_code == 200
    assert resp.json()["billing_code"] == "70553"


def test_get_procedure_not_found(client):
    resp = client.get("/api/v1/procedures/999")
    assert resp.status_code == 404
