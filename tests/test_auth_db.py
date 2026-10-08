from services.auth import AuthService
from services import db as dbmod


def test_auth_token_roundtrip():
    svc = AuthService()
    tok = svc.generate_token("test@example.com", "Test")
    assert "access_token" in tok
    payload = svc.verify_token(tok["access_token"])
    assert payload is not None
    assert payload["email"] == "test@example.com"


def test_db_session_not_none():
    assert dbmod.db_session is not None
    s = dbmod.db_session.get_session()
    try:
        assert s is not None
    finally:
        s.close()
