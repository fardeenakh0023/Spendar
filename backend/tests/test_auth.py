from app.models import UserSession
from app.core.security import utcnow
from datetime import timedelta
from tests.conftest import sign_up_and_login


def test_register_and_login(client):
    headers = sign_up_and_login(client)
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["username"] == "alice"
    assert "hashed_password" not in me.text
    assert headers["X-CSRF-Token"]


def test_register_seeds_default_categories(client):
    sign_up_and_login(client)
    assert len(client.get("/api/v1/categories").json()) >= 5


def test_duplicate_username_and_email(client):
    sign_up_and_login(client)
    r = client.post("/api/v1/auth/register", json={
        "username": "alice", "email": "other@example.com", "password": "password123"})
    assert r.status_code == 409
    r = client.post("/api/v1/auth/register", json={
        "username": "bob", "email": "ALICE@example.com", "password": "password123"})
    assert r.status_code == 409


def test_invalid_registration_input(client):
    r = client.post("/api/v1/auth/register", json={"username": "a", "email": "bad", "password": "short"})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_invalid_credentials(client):
    sign_up_and_login(client)
    client.cookies.clear()
    assert client.post("/api/v1/auth/login", json={"identifier": "alice", "password": "wrongpass1"}).status_code == 401
    assert client.post("/api/v1/auth/login", json={"identifier": "ghost", "password": "password123"}).status_code == 401


def test_login_with_email(client):
    sign_up_and_login(client)
    client.cookies.clear()
    r = client.post("/api/v1/auth/login", json={"identifier": "alice@example.com", "password": "password123"})
    assert r.status_code == 200


def test_protected_endpoints_require_login(client):
    for path in ["/auth/me", "/expenses", "/categories", "/dashboard/summary",
                 "/dashboard/category-breakdown", "/dashboard/history"]:
        assert client.get(f"/api/v1{path}").status_code == 401, path


def test_logout_ends_session(client):
    headers = sign_up_and_login(client)
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_write_requests_need_csrf_token(client):
    sign_up_and_login(client)
    r = client.post("/api/v1/categories", json={"name": "Gym"})
    assert r.status_code == 403
    r = client.post("/api/v1/categories", json={"name": "Gym"}, headers={"X-CSRF-Token": "wrong"})
    assert r.status_code == 403


def test_expired_session_is_rejected(client, db_session):
    sign_up_and_login(client)
    row = db_session.query(UserSession).first()
    row.expires_at = utcnow() - timedelta(minutes=1)
    db_session.commit()
    assert client.get("/api/v1/auth/me").status_code == 401
