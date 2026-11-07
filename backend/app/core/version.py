"""Application version utilities."""

from pathlib import Path

# Cache the version to avoid repeated filesystem access
_version: str | None = None


def get_version() -> str:
    """Get application version from VERSION file."""
    global _version
    if _version is not None:
        return _version

    # Look for VERSION file from project root
    # In development: project root is 3 levels up from this file
    # In AppImage: VERSION file is bundled at a known location
    current_dir = Path(__file__).resolve().parent

    # Check multiple possible locations
    possible_paths = [
        current_dir / ".." / ".." / ".." / "VERSION",  # development
        current_dir / ".." / ".." / "VERSION",  # alternative structure
        Path("/usr/share/beacon-lens/VERSION"),  # system install
        Path("/opt/beacon-lens/VERSION"),  # alternative system install
    ]

    for path in possible_paths:
        try:
            if path.exists():
                _version = path.read_text(encoding="utf-8").strip()
                return _version
        except OSError:
            continue

    # Fallback
    _version = "1.0.0"
    return _version


def get_app_info() -> dict[str, str]:
    """Get application info dict for health endpoint."""
    from app.core.config import get_settings

    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": get_version(),
        "environment": settings.app_env,
    }

