# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- OIDC/Keycloak authentication with PKCE flow
- JWT token validation with RS256 via Keycloak JWKS
- Role-based access control (viewer, operator, admin)
- Protected project API endpoints requiring authentication
- Frontend AuthContext with login/logout/callback handling
- Login page and OIDC callback component
- SPA PKCE flow with sessionStorage (no localStorage persistence)
- Auth integration in API client with automatic token injection

### Changed
- Project API endpoints now require valid Bearer token
- Navigation shows Sign In when unauthenticated, Projects/New Project when authenticated

### Fixed
- Test suite updated with auth dependency overrides

## [1.0.0] - 2026-10-12

### Added
- Repository initialized with core skeleton
- Backend: FastAPI app with `/health` endpoint
- Frontend: React + TypeScript + Vite app
- Docker Compose with backend, frontend, Keycloak, PostgreSQL (for Keycloak)
- pytest and Vitest test suites
- GitHub Actions CI workflow
- MIT License
- README with architecture, API reference, and AI/ML evaluation section