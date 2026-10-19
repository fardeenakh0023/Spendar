from tests.conftest import add_expense, first_category_id, sign_up_and_login


def seed(client, h):
    food = first_category_id(client)
    other = client.post("/api/v1/categories", headers=h, json={"name": "Gym"}).json()["id"]
    add_expense(client, h, food, "100.00", "2026-03-02")   # Monday
    add_expense(client, h, other, "50.50", "2026-03-08")   # Sunday of same week
    add_expense(client, h, food, "25.00", "2026-03-09")    # next Monday
    add_expense(client, h, food, "10.00", "2026-04-01")    # next month
    return food, other


def test_week_boundaries_are_monday_to_sunday(client):
    h = sign_up_and_login(client)
    seed(client, h)
    r = client.get("/api/v1/dashboard/summary?period=week&ref_date=2026-03-04").json()
    assert r["period"]["start_date"] == "2026-03-02" and r["period"]["end_date"] == "2026-03-08"
    assert r["total_spent"] == "150.50" and r["expense_count"] == 2


def test_month_and_year_totals(client):
    h = sign_up_and_login(client)
    seed(client, h)
    m = client.get("/api/v1/dashboard/summary?period=month&ref_date=2026-03-15").json()
    assert m["total_spent"] == "175.50" and m["expense_count"] == 3
    assert m["period"]["end_date"] == "2026-03-31"
    y = client.get("/api/v1/dashboard/summary?period=year&ref_date=2026-06-01").json()
    assert y["total_spent"] == "185.50" and y["expense_count"] == 4


def test_custom_range_is_inclusive(client):
    h = sign_up_and_login(client)
    seed(client, h)
    r = client.get("/api/v1/dashboard/summary?period=custom&start_date=2026-03-02&end_date=2026-03-09").json()
    assert r["expense_count"] == 3
    assert client.get("/api/v1/dashboard/summary?period=custom").status_code == 422
    assert client.get("/api/v1/dashboard/summary?period=decade").status_code == 422


def test_category_breakdown(client):
    h = sign_up_and_login(client)
    seed(client, h)
    r = client.get("/api/v1/dashboard/category-breakdown?period=month&ref_date=2026-03-15").json()
    cats = {c["category_name"]: c for c in r["categories"]}
    assert cats["Gym"]["total"] == "50.50"
    assert cats["Bills"]["total"] == "125.00" and cats["Bills"]["count"] == 2
    assert abs(sum(c["percentage"] for c in r["categories"]) - 100) < 0.5


def test_history_totals_ignore_pagination(client):
    h = sign_up_and_login(client)
    seed(client, h)
    r = client.get("/api/v1/dashboard/history?period=month&ref_date=2026-03-15&page=1&page_size=1").json()
    assert len(r["items"]) == 1
    assert r["total_spent"] == "175.50" and r["expense_count"] == 3


def test_dashboard_data_is_isolated(client, client2):
    h1 = sign_up_and_login(client, "alice")
    sign_up_and_login(client2, "bob")
    seed(client, h1)
    r = client2.get("/api/v1/dashboard/summary?period=year&ref_date=2026-03-15").json()
    assert r["total_spent"] == "0" or float(r["total_spent"]) == 0
    assert r["expense_count"] == 0
