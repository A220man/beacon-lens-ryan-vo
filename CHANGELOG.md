# Changelog

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — auth-oidc complete

### Added
- OIDC/Keycloak authentication with PKCE (Proof Key for Code Exchange)
- JWT token validation with RS256 via Keycloak JWKS endpoint
- Role-based access control (viewer, operator, admin) with `get_viewer`, `get_operator`, `get_admin` dependencies
- Protected project API endpoints requiring valid Bearer token
- Frontend `AuthProvider` with login/logout/callback handling
- Login page and OIDC callback component
- SPA PKCE flow storing verifier/state in `sessionStorage` (no `localStorage` token persistence)
- Auth integration in API client with automatic Bearer token injection
- Auth integration tests with real RSA-signed JWT tokens crossing the ASGI boundary
- Tests for token propagation into protected API endpoints (create/read projects)
- Tests for role denial (token without roles → 403)
- Tests for invalid/missing/mismatched token rejection (wrong issuer, wrong audience, expired, unknown key ID)

### Changed
- Project API endpoints now require valid Bearer token
- Navigation shows Sign In when unauthenticated, Projects/New Project when authenticated
- Test suite updated with auth dependency overrides

### Fixed
- `requirements.txt`: added `greenlet` dependency required by SQLAlchemy async engine
- `requirements.txt`: removed duplicate `httpx` entry
- `.gitignore`: un-ignored `frontend/package-lock.json` so it is tracked for CI

## [1.0.0] — 2026-10-12

### Added
- Repository initialized with core skeleton
- Backend: FastAPI app with `/health` endpoint
- Frontend: React + TypeScript + Vite app
- Project CRUD with SQLite persistence, pagination, filtering, validation
- ComfyUI local generation adapter with workflow submission and polling
- Fountain screenplay parser into structured scenes
- Storyboard engine: scene → prompt → image → PDF/JSON export
- Docker Compose with backend, frontend, Keycloak, PostgreSQL (for Keycloak)
- pytest and Vitest test suites
- GitHub Actions CI workflow
- MIT License
- README with architecture, API reference, and AI/ML evaluation section