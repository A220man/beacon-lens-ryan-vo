from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import httpx

from app.core.config import get_settings

settings = get_settings()

security = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    email: str | None = None
    preferred_username: str | None = None
    realm_access: dict[str, list[str]] | None = None
    resource_access: dict[str, dict[str, list[str]]] | None = None
    exp: int
    iat: int
    iss: str
    aud: str | list[str] | None = None

    def has_role(self, role: str) -> bool:
        if self.realm_access and role in self.realm_access.get("roles", []):
            return True
        if self.resource_access:
            for client_roles in self.resource_access.values():
                if role in client_roles.get("roles", []):
                    return True
        return False

    def has_any_role(self, roles: list[str]) -> bool:
        return any(self.has_role(r) for r in roles)


class JWKSClient:
    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url
        self._keys: dict[str, dict] | None = None
        self._fetched_at: datetime | None = None

    async def get_signing_key(self, kid: str) -> dict | None:
        await self._ensure_keys_fresh()
        return self._keys.get(kid) if self._keys else None

    async def _ensure_keys_fresh(self) -> None:
        now = datetime.now(UTC)
        if self._keys is not None and self._fetched_at is not None:
            if (now - self._fetched_at).total_seconds() < 3600:
                return
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(self.jwks_url)
            resp.raise_for_status()
            data = resp.json()
            self._keys = {key["kid"]: key for key in data.get("keys", [])}
            self._fetched_at = now


@lru_cache
def get_jwks_client() -> JWKSClient:
    return JWKSClient(settings.keycloak_jwks_url)


async def validate_oidc_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security)],
    jwks: Annotated[JWKSClient, Depends(get_jwks_client)],
) -> TokenPayload:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        signing_key = await jwks.get_signing_key(kid)
        if not signing_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find signing key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
            issuer=settings.keycloak_issuer,
            options={"verify_aud": True, "verify_iss": True, "verify_exp": True},
        )

        return TokenPayload(**payload)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach Keycloak for key validation",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: Annotated[TokenPayload, Depends(validate_oidc_token)],
) -> TokenPayload:
    return token


def require_roles(*roles: str):
    async def role_checker(
        token: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if not token.has_any_role(list(roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(roles)}",
            )
        return token

    return role_checker

async def get_viewer(
    token: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    if not token.has_any_role(["viewer", "operator", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires viewer role",
        )
    return token


async def get_operator(
    token: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    if not token.has_any_role(["operator", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires operator role",
        )
    return token


async def get_admin(
    token: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    if not token.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin role",
        )
    return token