from uuid import uuid4


def test_list_empty(client, auth_headers):
    r = client.get("/exhibits", headers=auth_headers)
    assert r.status_code == 200
    j = r.json()
    assert j["success"] is True
    assert j["data"] == []
    assert j["meta"]["total"] == 0


def test_create_and_get(client, auth_headers):
    body = {
        "title": "Composition with Red, Blue and Yellow",
        "artist": "Piet Mondrian",
        "year": 1930,
        "room": "Modern wing",
    }
    r = client.post("/exhibits", json=body, headers=auth_headers)
    assert r.status_code == 201
    j = r.json()
    assert j["success"] is True
    data = j["data"]
    assert data["title"] == body["title"]
    assert data["artist"] == body["artist"]
    assert data["year"] == body["year"]
    assert data["room"] == body["room"]
    eid = data["id"]

    r2 = client.get(f"/exhibits/{eid}", headers=auth_headers)
    assert r2.status_code == 200
    d2 = r2.json()["data"]
    assert d2["title"] == body["title"]


def test_get_missing_returns_404(client, auth_headers):
    r = client.get(f"/exhibits/{uuid4()}", headers=auth_headers)
    assert r.status_code == 404
    j = r.json()
    assert j["success"] is False
    assert j["error"]["code"] == "EXHIBIT_NOT_FOUND"


def test_filter_by_room(client, auth_headers):
    client.post(
        "/exhibits",
        json={
            "title": "A",
            "artist": "X",
            "year": 1900,
            "room": "North",
        },
        headers=auth_headers,
    )
    client.post(
        "/exhibits",
        json={
            "title": "B",
            "artist": "Y",
            "year": 1901,
            "room": "South",
        },
        headers=auth_headers,
    )
    r = client.get("/exhibits", params={"room": "north"}, headers=auth_headers)
    assert r.status_code == 200
    rows = r.json()["data"]
    assert len(rows) == 1
    assert rows[0]["title"] == "A"


def test_year_range(client, auth_headers):
    client.post(
        "/exhibits",
        json={"title": "Old", "artist": "A", "year": 1800, "room": "R1"},
        headers=auth_headers,
    )
    client.post(
        "/exhibits",
        json={"title": "New", "artist": "B", "year": 2000, "room": "R1"},
        headers=auth_headers,
    )
    r = client.get(
        "/exhibits",
        params={"year_from": 1900, "year_to": 1999},
        headers=auth_headers,
    )
    assert len(r.json()["data"]) == 0
    r2 = client.get("/exhibits", params={"year_from": 1990}, headers=auth_headers)
    titles = {x["title"] for x in r2.json()["data"]}
    assert titles == {"New"}


def test_patch(client, auth_headers):
    r = client.post(
        "/exhibits",
        json={
            "title": "Temp",
            "artist": "Someone",
            "year": 1920,
            "room": "Hall",
        },
        headers=auth_headers,
    )
    eid = r.json()["data"]["id"]
    r2 = client.patch(f"/exhibits/{eid}", json={"room": "East gallery"}, headers=auth_headers)
    assert r2.status_code == 200
    d = r2.json()["data"]
    assert d["room"] == "East gallery"
    assert d["title"] == "Temp"


def test_delete(client, auth_headers):
    r = client.post(
        "/exhibits",
        json={
            "title": "Gone",
            "artist": "Z",
            "year": 1950,
            "room": "R",
        },
        headers=auth_headers,
    )
    eid = r.json()["data"]["id"]
    r2 = client.delete(f"/exhibits/{eid}", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["success"] is True
    r3 = client.get(f"/exhibits/{eid}", headers=auth_headers)
    assert r3.status_code == 404


def test_rooms_summary(client, auth_headers):
    client.post(
        "/exhibits",
        json={"title": "1", "artist": "a", "year": 1900, "room": "Alpha"},
        headers=auth_headers,
    )
    client.post(
        "/exhibits",
        json={"title": "2", "artist": "b", "year": 1901, "room": "Alpha"},
        headers=auth_headers,
    )
    client.post(
        "/exhibits",
        json={"title": "3", "artist": "c", "year": 1902, "room": "Beta"},
        headers=auth_headers,
    )
    r = client.get("/exhibits/rooms/summary", headers=auth_headers)
    assert r.status_code == 200
    rows = r.json()["data"]
    by_name = {x["name"]: x["count"] for x in rows}
    assert by_name["Alpha"] == 2
    assert by_name["Beta"] == 1


def test_validation_rejects_bad_year(client, auth_headers):
    r = client.post(
        "/exhibits",
        json={
            "title": "Bad",
            "artist": "X",
            "year": 3000,
            "room": "R",
        },
        headers=auth_headers,
    )
    assert r.status_code == 422
    j = r.json()
    assert j["success"] is False
    assert j["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in j["error"]
