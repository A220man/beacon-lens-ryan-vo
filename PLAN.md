# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

linux-packaging

## Roadmap

### core-skeleton — FastAPI/React skeleton with health check

Status: done

Acceptance:
- Backend serves /health endpoint returning 200 OK
- Frontend builds and serves React app
- Docker compose brings up both services
- Basic pytest and vitest tests pass

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/core/security.py`, `backend/requirements.txt`, `backend/Dockerfile`, `backend/.dockerignore`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`, `frontend/src/components/HealthBadge.tsx`, `frontend/src/api/client.ts`, `frontend/vite.config.ts`, `frontend/Dockerfile`, `frontend/.dockerignore`, `frontend/nginx.conf`, `compose.yaml`, `pyproject.toml`, `.env.example`, `.gitignore`, `README.md`, `LICENSE`, `CHANGELOG.md`, `portfolio.json`, `keycloak/realm-export.json`

Tests: `backend/tests/test_health.py`, `backend/tests/conftest.py`, `frontend/src/App.test.tsx`, `frontend/src/test/setup.ts`

### project-management — Project CRUD with SQLite persistence

Status: done

Acceptance:
- Create/list/get/update/delete projects via API
- Projects stored in SQLite with UTC timestamps
- Pagination and filtering on list endpoint
- Validation on create/update

Implementation: `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`, `backend/app/api/projects.py`, `backend/app/api/__init__.py`, `backend/app/services/__init__.py`

Tests: `backend/tests/test_projects.py`

### comfyui-adapter — ComfyUI local generation adapter

Status: done

Acceptance:
- Configure ComfyUI endpoint in project settings
- Submit prompt workflow to ComfyUI API
- Poll for completion and retrieve generated images
- Store generation history linked to project

Implementation: `backend/app/services/comfyui.py`, `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`

Tests: `backend/tests/test_comfyui.py`

### storyboard-workflow — Fountain script to storyboard workflow

Status: done

Acceptance:
- Parse Fountain format script into scenes
- Generate storyboard frames per scene via ComfyUI
- Export storyboard as PDF/JSON
- Frontend storyboard editor with scene navigation

Implementation: `backend/app/services/fountain.py`, `backend/app/services/storyboard.py`, `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`

Tests: `backend/tests/test_fountain.py`, `backend/tests/test_storyboard.py`

### auth-oidc — OIDC/Keycloak authentication

Status: done

Acceptance:
- Keycloak realm import provided
- Backend validates JWT tokens with RS256 via Keycloak JWKS
- Frontend PKCE login flow with Keycloak
- Protected API endpoints require auth
- OIDC login/callback integration test through ASGI boundary with real RSA-signed JWT tokens

Implementation: `backend/app/core/auth.py`, `backend/app/api/projects.py`, `frontend/src/auth/config.ts`, `frontend/src/auth/pkce.ts`, `frontend/src/auth/service.ts`, `frontend/src/auth/context.tsx`, `frontend/src/components/Callback.tsx`, `frontend/src/components/LoginPage.tsx`, `keycloak/realm-export.json`

Tests: `backend/tests/test_auth.py`, `backend/tests/conftest.py`, `backend/tests/test_auth_integration.py`

### linux-packaging — AppImage and Linux packaging

Status: done

Acceptance:
- Dockerfile produces AppImage via linuxdeploy
- DEB and RPM packages build in CI
- Frontend bundled as static assets
- Single binary runs on Linux without install

Implementation: `backend/Dockerfile.appimage`, `backend/app/main.py`, `.github/workflows/release.yml`, `packaging/test_appimage.sh`

Tests: `packaging/test_appimage.sh`, `backend/tests/test_health.py`

