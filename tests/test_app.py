from app import app

def test_health():
    with app.test_client() as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

def test_orice():
    with app.test_client() as c:
        r = c.get("/")
        assert r.status_code == 200
        assert r.get_json()["name"] == "Vlad"

