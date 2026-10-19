import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield session
    session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    return TestClient(app)


@pytest.fixture()
def client2(db_session):
    """A second browser with its own cookie jar (a different user)."""
    return TestClient(app)


def sign_up_and_login(client: TestClient, username="alice", password="password123") -> dict:
    """Register + log in. Returns the CSRF header dict to use on write requests."""
    r = client.post("/api/v1/auth/register", json={
        "username": username, "email": f"{username}@example.com", "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/auth/login", json={"identifier": username, "password": password})
    assert r.status_code == 200, r.text
    return {"X-CSRF-Token": r.json()["csrf_token"]}


def first_category_id(client: TestClient) -> int:
    return client.get("/api/v1/categories").json()[0]["id"]


def add_expense(client, headers, cat_id, amount="10.00", day="2026-03-04", desc="Lunch"):
    r = client.post("/api/v1/expenses", headers=headers, json={
        "description": desc, "amount": amount, "category_id": cat_id, "expense_date": day})
    assert r.status_code == 201, r.text
    return r.json()
