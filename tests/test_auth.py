def test_post_without_bearer_returns_403(client):
    r = client.post(
        "/exhibits",
        json={
            "title": "X",
            "artist": "Y",
            "year": 1900,
            "room": "R",
        },
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "AUTH_REQUIRED"


def test_get_exhibits_without_bearer_returns_403(client):
    r = client.get("/exhibits")
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "AUTH_REQUIRED"


def test_post_with_wrong_token_returns_401(client):
    r = client.post(
        "/exhibits",
        json={
            "title": "X",
            "artist": "Y",
            "year": 1900,
            "room": "R",
        },
        headers={"Authorization": "Bearer wrong"},
    )
    assert r.status_code == 401
    j = r.json()
    assert j["success"] is False
    assert j["error"]["code"] == "AUTH_INVALID_CREDENTIALS"
    assert j["message"] == "Invalid credentials"
