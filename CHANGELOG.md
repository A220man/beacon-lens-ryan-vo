# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold: FastAPI backend, React frontend, Docker Compose
- Health check endpoint (`GET /health`)
- SQLite database setup with SQLAlchemy 2.0
- Project CRUD models and API (planned)
- ComfyUI adapter service (planned)
- Fountain script parser (planned)
- Storyboard generation workflow (planned)
- OIDC/Keycloak authentication (planned)
- Linux AppImage/DEB/RPM packaging (planned)

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