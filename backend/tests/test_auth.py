from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.auth import JWKSClient, TokenPayload, validate_oidc_token


class TestTokenPayload:
    def test_has_role_realm_access(self):
        token = TokenPayload(
            sub="user1",
            realm_access={"roles": ["viewer", "operator"]},
            resource_access={},
            exp=9999999999,
            iat=0,
            iss="http://test/realms/test",
            aud="test",
        )
        assert token.has_role("viewer") is True
        assert token.has_role("operator") is True
        assert token.has_role("admin") is False

    def test_has_role_resource_access(self):
        token = TokenPayload(
            sub="user1",
            realm_access={},
            resource_access={"test-client": {"roles": ["admin"]}},
            exp=9999999999,
            iat=0,
            iss="http://test/realms/test",
            aud="test",
        )
        assert token.has_role("admin") is True

    def test_has_any_role(self):
        token = TokenPayload(
            sub="user1",
            realm_access={"roles": ["viewer"]},
            resource_access={},
            exp=9999999999,
            iat=0,
            iss="http://test/realms/test",
            aud="test",
        )
        assert token.has_any_role(["viewer", "operator"]) is True
        assert token.has_any_role(["operator", "admin"]) is False


class TestJWKSClient:
    @pytest.mark.asyncio
    async def test_get_signing_key_caches_keys(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "keys": [
                {"kid": "key1", "kty": "RSA", "n": "test", "e": "AQAB"},
                {"kid": "key2", "kty": "RSA", "n": "test2", "e": "AQAB"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            client = JWKSClient("http://test/jwks")
            key1 = await client.get_signing_key("key1")
            key2 = await client.get_signing_key("key2")

            assert key1 is not None
            assert key1["kid"] == "key1"
            assert key2 is not None
            assert key2["kid"] == "key2"
            # Second call should use cache
            assert mock_get.call_count == 1

    @pytest.mark.asyncio
    async def test_get_signing_key_not_found(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            client = JWKSClient("http://test/jwks")
            key = await client.get_signing_key("nonexistent")
            assert key is None


class TestValidateOIDCToken:
    @pytest.mark.asyncio
    async def test_validate_token_missing_header(self):
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        with pytest.raises(HTTPException) as exc:
            await validate_oidc_token(None, JWKSClient("http://test/jwks"))
        assert exc.value.status_code == 401
        assert "Missing authorization header" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_token_missing_kid(self):
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.no_kid")
        with patch("jose.jwt.get_unverified_header", return_value={}):
            with pytest.raises(HTTPException) as exc:
                await validate_oidc_token(credentials, JWKSClient("http://test/jwks"))
        assert exc.value.status_code == 401
        assert "Token missing key ID" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_token_key_not_found(self):
        from datetime import UTC, datetime
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        jwks = JWKSClient("http://test/jwks")
        jwks._keys = {}
        jwks._fetched_at = datetime.now(UTC)

        with patch("jose.jwt.get_unverified_header", return_value={"kid": "missing"}):
            with pytest.raises(HTTPException) as exc:
                await validate_oidc_token(credentials, jwks)
        assert exc.value.status_code == 401
        assert "Unable to find signing key" in exc.value.detail