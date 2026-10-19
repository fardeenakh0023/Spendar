from tests.conftest import add_expense, first_category_id, sign_up_and_login


def test_create_and_list_category(client):
    h = sign_up_and_login(client)
    r = client.post("/api/v1/categories", headers=h, json={"name": "  Gym  "})
    assert r.status_code == 201
    assert r.json()["name"] == "Gym"
    names = [c["name"] for c in client.get("/api/v1/categories").json()]
    assert "Gym" in names


def test_duplicate_and_empty_category(client):
    h = sign_up_and_login(client)
    client.post("/api/v1/categories", headers=h, json={"name": "Gym"})
    assert client.post("/api/v1/categories", headers=h, json={"name": "Gym"}).status_code == 409
    assert client.post("/api/v1/categories", headers=h, json={"name": "   "}).status_code == 422


def test_rename_category(client):
    h = sign_up_and_login(client)
    cid = client.post("/api/v1/categories", headers=h, json={"name": "Gym"}).json()["id"]
    r = client.patch(f"/api/v1/categories/{cid}", headers=h, json={"name": "Fitness"})
    assert r.status_code == 200 and r.json()["name"] == "Fitness"
    clash = client.patch(f"/api/v1/categories/{cid}", headers=h, json={"name": "Food"})
    assert clash.status_code == 409


def test_cannot_delete_category_in_use(client):
    h = sign_up_and_login(client)
    cid = first_category_id(client)
    add_expense(client, h, cid)
    r = client.delete(f"/api/v1/categories/{cid}", headers=h)
    assert r.status_code == 409


def test_delete_unused_category(client):
    h = sign_up_and_login(client)
    cid = client.post("/api/v1/categories", headers=h, json={"name": "Gym"}).json()["id"]
    assert client.delete(f"/api/v1/categories/{cid}", headers=h).status_code == 204
    assert client.delete(f"/api/v1/categories/{cid}", headers=h).status_code == 404


def test_other_users_category_is_hidden(client, client2):
    h1 = sign_up_and_login(client, "alice")
    h2 = sign_up_and_login(client2, "bob")
    cid = first_category_id(client)
    assert client2.patch(f"/api/v1/categories/{cid}", headers=h2, json={"name": "Hacked"}).status_code == 404
    assert client2.delete(f"/api/v1/categories/{cid}", headers=h2).status_code == 404
    bob_ids = {c["id"] for c in client2.get("/api/v1/categories").json()}
    assert cid not in bob_ids
