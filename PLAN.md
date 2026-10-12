# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-management

## Roadmap

### core-skeleton — FastAPI/React skeleton with health check

Status: done

Acceptance:
- Backend serves /health endpoint returning 200 OK
- Frontend builds and serves React app
- Docker compose brings up both services
- Basic pytest and vitest tests pass

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/core/security.py`, `backend/requirements.txt`, `backend/Dockerfile`, `backend/.dockerignore`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`, `frontend/src/components/HealthBadge.tsx`, `frontend/src/api/client.ts`, `frontend/vite.config.ts`, `frontend/Dockerfile`, `frontend/.dockerignore`, `frontend/nginx.conf`, `compose.yaml`, `pyproject.toml`, `.env.example`, `.gitignore`, `README.md`, `LICENSE`, `CHANGELOG.md`, `portfolio.json`, `keycloak/realm-export.json`

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

Status: planned

Acceptance:
- Keycloak realm import provided
- Backend validates JWT tokens with roles
- Frontend PKCE login flow with Keycloak
- Protected API endpoints require auth

Implementation: `backend/app/core/auth.py`, `backend/app/api/auth.py`, `frontend/src/auth/`, `keycloak/realm-export.json`

Tests: `backend/tests/test_auth.py`

### linux-packaging — AppImage and Linux packaging

Status: planned

Acceptance:
- Dockerfile produces AppImage via linuxdeploy
- DEB and RPM packages build in CI
- Frontend bundled as static assets
- Single binary runs on Linux without install

Implementation: `backend/Dockerfile.appimage`, `.github/workflows/release.yml`, `packaging/`

Tests: `packaging/test_appimage.sh`

