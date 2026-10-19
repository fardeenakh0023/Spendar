from tests.conftest import add_expense, first_category_id, sign_up_and_login


def test_expense_crud(client):
    h = sign_up_and_login(client)
    cid = first_category_id(client)
    exp = add_expense(client, h, cid, amount="12.50", desc="Coffee")
    assert exp["amount"] == "12.50" and exp["category_name"]

    assert client.get(f"/api/v1/expenses/{exp['id']}").json()["description"] == "Coffee"

    r = client.patch(f"/api/v1/expenses/{exp['id']}", headers=h, json={"amount": "20.00", "description": "Big coffee"})
    assert r.status_code == 200 and r.json()["amount"] == "20.00"

    page = client.get("/api/v1/expenses").json()
    assert page["total"] == 1 and page["items"][0]["description"] == "Big coffee"

    assert client.delete(f"/api/v1/expenses/{exp['id']}", headers=h).status_code == 204
    assert client.get(f"/api/v1/expenses/{exp['id']}").status_code == 404


def test_invalid_amounts_and_missing_fields(client):
    h = sign_up_and_login(client)
    cid = first_category_id(client)
    base = {"description": "x", "amount": "5", "category_id": cid, "expense_date": "2026-03-04"}
    for bad in [{"amount": "0"}, {"amount": "-3"}, {"amount": "abc"}, {"amount": "1.234"},
                {"description": "   "}, {"expense_date": "2026-13-45"}]:
        r = client.post("/api/v1/expenses", headers=h, json={**base, **bad})
        assert r.status_code == 422, bad
    r = client.post("/api/v1/expenses", headers=h, json={"description": "x"})
    assert r.status_code == 422


def test_category_must_exist_and_belong_to_user(client, client2):
    h1 = sign_up_and_login(client, "alice")
    h2 = sign_up_and_login(client2, "bob")
    alice_cat = first_category_id(client)
    r = client2.post("/api/v1/expenses", headers=h2, json={
        "description": "x", "amount": "5", "category_id": alice_cat, "expense_date": "2026-03-04"})
    assert r.status_code == 422
    r = client.post("/api/v1/expenses", headers=h1, json={
        "description": "x", "amount": "5", "category_id": 99999, "expense_date": "2026-03-04"})
    assert r.status_code == 422


def test_user_cannot_touch_other_users_expenses(client, client2):
    h1 = sign_up_and_login(client, "alice")
    h2 = sign_up_and_login(client2, "bob")
    exp = add_expense(client, h1, first_category_id(client))
    url = f"/api/v1/expenses/{exp['id']}"
    assert client2.get(url).status_code == 404
    assert client2.patch(url, headers=h2, json={"amount": "1.00"}).status_code == 404
    assert client2.delete(url, headers=h2).status_code == 404
    assert client2.get("/api/v1/expenses").json()["total"] == 0
    assert client.get(url).status_code == 200  # still intact


def test_pagination_and_filters(client):
    h = sign_up_and_login(client)
    cid = first_category_id(client)
    for i in range(1, 8):
        add_expense(client, h, cid, day=f"2026-03-0{i}", desc=f"e{i}")
    page2 = client.get("/api/v1/expenses?page=2&page_size=3").json()
    assert page2["total"] == 7 and len(page2["items"]) == 3
    ranged = client.get("/api/v1/expenses?start_date=2026-03-03&end_date=2026-03-05").json()
    assert ranged["total"] == 3
    assert client.get("/api/v1/expenses?start_date=2026-03-05&end_date=2026-03-01").status_code == 422
