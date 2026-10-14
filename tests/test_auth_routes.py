import uuid

from fastapi.testclient import TestClient

from app import app
from models import Customer, User
from services.auth import AuthService
from services.db import SessionLocal

PASSWORD = "supersecret1"


def unique_email(prefix: str = "auth-test") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


def test_password_hashing_roundtrip():
    svc = AuthService()
    hashed = svc.hash_password(PASSWORD)

    assert hashed != PASSWORD
    assert svc.verify_password(PASSWORD, hashed)
    assert not svc.verify_password("wrong-password", hashed)
    assert not svc.verify_password(PASSWORD, "")
    # two hashes of the same password differ (per-password salt)
    assert svc.hash_password(PASSWORD) != hashed


def test_register_login_and_protected_writes():
    email = unique_email()
    customer_email = unique_email("customer")
    client = TestClient(app)

    try:
        # register
        res = client.post(
            "/api/auth/register",
            json={"name": "Auth Test", "email": email, "password": PASSWORD},
        )
        assert res.status_code == 201, res.text
        body = res.json()
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == email
        headers = {"Authorization": f"Bearer {body['access_token']}"}

        # duplicate email is rejected
        res = client.post("/api/auth/register", json={"email": email, "password": PASSWORD})
        assert res.status_code == 409

        # weak password is rejected by schema validation
        res = client.post(
            "/api/auth/register",
            json={"email": unique_email("weak"), "password": "short"},
        )
        assert res.status_code == 422

        # login with the right password works
        res = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
        assert res.status_code == 200, res.text
        login_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

        # wrong password / unknown user are rejected
        assert (
            client.post(
                "/api/auth/login", json={"email": email, "password": "wrong-password"}
            ).status_code
            == 401
        )
        assert (
            client.post(
                "/api/auth/login",
                json={"email": unique_email("nobody"), "password": PASSWORD},
            ).status_code
            == 401
        )

        # token resolves to the right user
        me = client.get("/api/auth/me", headers=login_headers)
        assert me.status_code == 200
        assert me.json() == {**body["user"], "name": "Auth Test"}

        # protected writes need a token, and work with one
        assert (
            client.post(
                "/api/customers", json={"name": "Auth Test", "email": customer_email}
            ).status_code
            == 401
        )
        created = client.post(
            "/api/customers",
            json={"name": "Auth Test", "email": customer_email},
            headers=headers,
        )
        assert created.status_code == 201, created.text

        # a garbage token is rejected
        assert (
            client.get(
                "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
            ).status_code
            == 401
        )
    finally:
        with SessionLocal() as session:
            session.query(Customer).filter(Customer.email == customer_email).delete(
                synchronize_session=False
            )
            session.query(User).filter(User.email == email).delete(synchronize_session=False)
            session.commit()


def test_legacy_token_without_user_is_rejected():
    """A valid JWT for a user that no longer exists must not authenticate."""
    svc = AuthService()
    token = svc.generate_token("ghost-user@example.com", "Ghost")["access_token"]

    client = TestClient(app)
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
