import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base
from main import app, get_db

TEST_DB = "sqlite:///./test_test.db"

if os.path.exists("test_test.db"):
    os.remove("test_test.db")

engine = create_engine(
    TEST_DB,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def cleanup_session():
    yield
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def register_user(
    client: TestClient,
    name: str,
    email: str,
    password: str = "secret123",
):
    return client.post(
        "/users/",
        json={"name": name, "email": email, "password": password},
    )


def login_user(client: TestClient, email: str, password: str = "secret123"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_create_user(client: TestClient):
    response = register_user(client, name="Alice", email="alice@example.com")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_duplicate_email(client: TestClient):
    register_user(client, name="Bob", email="bob@example.com")
    response = register_user(client, name="Bob Two", email="bob@example.com")

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_returns_bearer_token(client: TestClient):
    register_user(client, name="Carol", email="carol@example.com")
    response = login_user(client, email="carol@example.com")

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["expires_at"]


def test_login_rejects_wrong_password(client: TestClient):
    register_user(client, name="Dave", email="dave@example.com")
    response = login_user(client, email="dave@example.com", password="wrong123")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_create_post_requires_authentication(client: TestClient):
    user_response = register_user(client, name="Eve", email="eve@example.com")
    user_id = user_response.json()["id"]

    no_auth_response = client.post(
        f"/users/{user_id}/posts",
        json={"title": "Hello", "content": "World"},
    )

    login_response = login_user(client, email="eve@example.com")
    token = login_response.json()["access_token"]
    auth_response = client.post(
        f"/users/{user_id}/posts",
        json={"title": "Hello", "content": "World"},
        headers=auth_headers(token),
    )

    assert no_auth_response.status_code == 401
    assert auth_response.status_code == 200
    assert auth_response.json()["author_id"] == user_id


def test_user_cannot_create_post_for_another_user(client: TestClient):
    first_user = register_user(client, name="Frank", email="frank@example.com")
    second_user = register_user(client, name="Grace", email="grace@example.com")

    token = login_user(client, email="frank@example.com").json()["access_token"]
    response = client.post(
        f"/users/{second_user.json()['id']}/posts",
        json={"title": "Nope", "content": "Not your account"},
        headers=auth_headers(token),
    )

    assert first_user.json()["id"] != second_user.json()["id"]
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_list_users_and_posts(client: TestClient):
    user_id = register_user(client, name="Hank", email="hank@example.com").json()["id"]
    token = login_user(client, email="hank@example.com").json()["access_token"]

    client.post(
        f"/users/{user_id}/posts",
        json={"title": "First post", "content": "Simple and working"},
        headers=auth_headers(token),
    )

    users_response = client.get("/users/")
    posts_response = client.get("/posts")

    assert users_response.status_code == 200
    assert posts_response.status_code == 200
    assert len(users_response.json()) == 1
    assert len(posts_response.json()) == 1
