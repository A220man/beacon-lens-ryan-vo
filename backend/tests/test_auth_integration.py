"""Integration tests for OIDC token validation through the ASGI boundary.

Generates a real RSA key pair, builds a JWKS response, and signs JWT tokens
that exercise the full validate_oidc_token -> get_current_user -> get_viewer
dependency chain via FastAPI's dependency injection through the ASGI app.
"""
import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from jose import jwt as jose_jwt

from app.core.auth import get_jwks_client
from app.core.database import get_db
from app.main import app

# ---------------------------------------------------------------------------
# Test RSA key pair (generated once at import time for speed)
# ---------------------------------------------------------------------------
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIVATE_PEM = _PRIVATE_KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
_PUB_NUMBERS = _PRIVATE_KEY.public_key().public_numbers()

KID = "test-integration-key"
# These match the default Settings values (no .env in test env)
ISSUER = "http://localhost:8080/realms/beacon-lens"
AUDIENCE = "beacon-lens-frontend"


def _b64url_uint(n: int) -> str:
    """Encode a big-endian integer as base64url without padding (JWK style)."""
    byte_len = (n.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(n.to_bytes(byte_len, "big")).decode("ascii").rstrip("=")


TEST_JWKS: dict[str, Any] = {
    "keys": [
        {
            "kid": KID,
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": _b64url_uint(_PUB_NUMBERS.n),
            "e": _b64url_uint(_PUB_NUMBERS.e),
        }
    ]
}


class _StaticJWKSClient:
    """Stand-in for JWKSClient that returns pre-built keys without HTTP."""

    def __init__(self, jwks: dict[str, Any]) -> None:
        self._keys: dict[str, dict[str, Any]] = {
            k["kid"]: k for k in jwks.get("keys", [])
        }

    async def get_signing_key(self, kid: str) -> dict[str, Any] | None:
        return self._keys.get(kid)

    async def _ensure_keys_fresh(self) -> None:
        pass


def _make_token(
    roles: list[str] | None = None,
    *,
    sub: str = "test-user",
    aud: str = AUDIENCE,
    iss: str = ISSUER,
    expire_hours: float = 1,
    kid: str = KID,
    extra: dict[str, Any] | None = None,
) -> str:
    """Sign a JWT with the test RSA private key."""
    payload: dict[str, Any] = {
        "sub": sub,
        "email": "test@example.com",
        "preferred_username": "testuser",
        "aud": aud,
        "iss": iss,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=expire_hours),
    }
    if roles:
        payload["realm_access"] = {"roles": roles}
        payload["resource_access"] = {}
    if extra:
        payload.update(extra)
    return jose_jwt.encode(payload, _PRIVATE_PEM, algorithm="RS256", headers={"kid": kid})


@pytest.fixture
async def auth_client(db_session):
    """ASGI test client with *real* OIDC token validation (no role mocking).

    Overrides only the DB session and JWKS client.  All other auth
    dependencies (validate_oidc_token, get_current_user, get_viewer) run
    for real, exercising the full security dependency chain.
    """

    def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_jwks_client] = lambda: _StaticJWKSClient(TEST_JWKS)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


class TestOIDCAuthIntegration:
    """Token-based auth: propagation, rejection, and role denial."""

    @pytest.mark.asyncio
    async def test_valid_token_accesses_protected_endpoint(self, auth_client):
        """A well-formed token with the viewer role can list projects."""
        token = _make_token(roles=["viewer"])
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_valid_token_creates_project(self, auth_client):
        """Token propagation into a write operation succeeds."""
        token = _make_token(roles=["viewer"])
        resp = await auth_client.post(
            "/api/v1/projects",
            json={"name": "Auth Integration Project", "description": "Created via valid JWT"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Auth Integration Project"
        assert data["description"] == "Created via valid JWT"

    @pytest.mark.asyncio
    async def test_missing_token_rejected(self, auth_client):
        """No Authorization header → 401."""
        resp = await auth_client.get("/api/v1/projects")
        assert resp.status_code == 401
        assert "authorization" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_malformed_token_rejected(self, auth_client):
        """Garbage Bearer token → 401."""
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_token_wrong_kid_rejected(self, auth_client):
        """Token signed with an unregistered key ID → 401."""
        token = _make_token(roles=["viewer"], kid="unknown-key-id")
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401
        assert "signing key" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_token_wrong_issuer_rejected(self, auth_client):
        """Token with wrong issuer → 401."""
        token = _make_token(roles=["viewer"], iss="http://evil.example/realms/evil")
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_token_wrong_audience_rejected(self, auth_client):
        """Token with wrong audience → 401."""
        token = _make_token(roles=["viewer"], aud="wrong-client-id")
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, auth_client):
        """Expired token → 401."""
        token = _make_token(roles=["viewer"], expire_hours=-1)
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_token_without_roles_denied(self, auth_client):
        """Token with no realm/roles → 403 (role denial)."""
        token = _make_token(roles=None)
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert "viewer" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_token_with_operator_role_accesses(self, auth_client):
        """Operator role is accepted by the viewer-gated endpoint."""
        token = _make_token(roles=["operator"])
        resp = await auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_valid_token_get_project(self, auth_client):
        """Token propagation into a GET-by-id read operation."""
        # Create a project first
        token = _make_token(roles=["viewer"])
        create_resp = await auth_client.post(
            "/api/v1/projects",
            json={"name": "Read Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        project_id = create_resp.json()["id"]

        # Fetch it back with the same token
        resp = await auth_client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Read Test"