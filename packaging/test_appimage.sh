#!/bin/bash
# Test script for AppImage functionality
# This script validates that the AppImage can be extracted and run

set -e

APPIMAGE_PATH="${1:-./beacon-lens.AppImage}"

if [[ ! -f "$APPIMAGE_PATH" ]]; then
    echo "Error: AppImage not found at $APPIMAGE_PATH"
    exit 1
fi

echo "Testing AppImage: $APPIMAGE_PATH"

# Make executable
chmod +x "$APPIMAGE_PATH"

# Test extraction
echo "Extracting AppImage..."
EXTRACT_DIR="./appimage-extract"
rm -rf "$EXTRACT_DIR"
"$APPIMAGE_PATH" --appimage-extract > /dev/null 2>&1
mv squashfs-root "$EXTRACT_DIR"

echo "AppImage extracted to $EXTRACT_DIR"

# Verify structure
echo "Verifying AppDir structure..."
if [[ ! -f "$EXTRACT_DIR/usr/bin/beacon-lens" ]]; then
    echo "Error: Entry point not found"
    exit 1
fi

if [[ ! -f "$EXTRACT_DIR/usr/share/applications/beacon-lens.desktop" ]]; then
    echo "Error: Desktop entry not found"
    exit 1
fi

if [[ ! -f "$EXTRACT_DIR/usr/share/icons/hicolor/256x256/apps/beacon-lens.svg" ]]; then
    echo "Error: Icon not found"
    exit 1
fi

if [[ ! -f "$EXTRACT_DIR/usr/share/metainfo/beacon-lens.metainfo.xml" ]]; then
    echo "Error: AppStream metadata not found"
    exit 1
fi

# Check Python packages
if [[ ! -d "$EXTRACT_DIR/usr/lib/python3.12/site-packages/app" ]]; then
    echo "Error: Application code not bundled"
    exit 1
fi

# Check key dependencies
if [[ ! -d "$EXTRACT_DIR/usr/lib/python3.12/site-packages/fastapi" ]]; then
    echo "Error: FastAPI not bundled"
    exit 1
fi

if [[ ! -d "$EXTRACT_DIR/usr/lib/python3.12/site-packages/uvicorn" ]]; then
    echo "Error: Uvicorn not bundled"
    exit 1
fi

echo "All structure checks passed!"

# Test that the entrypoint script is valid
echo "Checking entrypoint script..."
if ! grep -q "uvicorn app.main:app" "$EXTRACT_DIR/usr/bin/beacon-lens"; then
    echo "Error: Entrypoint doesn't start uvicorn correctly"
    exit 1
fi

echo "Entrypoint script looks correct!"

# Cleanup
rm -rf "$EXTRACT_DIR"

echo "AppImage test passed!"
