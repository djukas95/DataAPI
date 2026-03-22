def test_health(client, auth_headers):
    r = client.get("/health", headers=auth_headers)
    assert r.status_code == 200
    j = r.json()
    assert j["success"] is True
    assert j["message"] == "Service healthy"
    assert j["data"] == {"status": "ok"}


def test_health_without_token_returns_403(client):
    r = client.get("/health")
    assert r.status_code == 403
    j = r.json()
    assert j["success"] is False
    assert j["error"]["code"] == "AUTH_REQUIRED"
