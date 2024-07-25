#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: Build linux binaries for psmonitor."
    echo
    echo "Example:"
    echo "  $0 <build-type>"
    echo
    echo "Available build types (at least one is required):"
    echo "  - desktop : Build the desktop application with the server included."
    echo "  - server  : Build the standalone server only."
    echo
    exit 1
fi

BUILD_TYPE="$1"

# Set conditional spec file based on the build type
if [ "$BUILD_TYPE" == "server" ]; then
    BUILD_SPEC="psmonitor_server.spec"
else
    BUILD_SPEC="psmonitor.spec"
fi

# Get the current directory
PWD=$(pwd)

BUILD_DIR="$PWD/build"
DIST_DIR="$PWD/dist"

PKG_DIR="$PWD/package"
SPEC_FILE="$PKG_DIR/$BUILD_TYPE/linux/$BUILD_SPEC"

UPX_VER="upx-4.2.1-win64"

# Check for UPX
echo "Checking for UPX..."
if [ ! -d "$PKG_DIR/$UPX_VER" ]; then
    echo "Downloading UPX"
    curl -L "https://github.com/upx/upx/releases/download/v4.2.1/$UPX_VER.tar.xz" -o "$PKG_DIR"
    tar -xf "$PKG_DIR/$UPX_VER.tar.xz" -C "$PKG_DIR"
    rm -f "$PKG_DIR/$UPX_VER.tar.xz"
else
    echo "UPX is available"
fi

# Check build dir
if [ -d "$BUILD_DIR" ]; then
    echo "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
fi

# Check dist dir
if [ -d "$DIST_DIR" ]; then
    echo "Cleaning dist directory..."
    rm -rf "$DIST_DIR"
fi

echo "Building psmonitor..."
pyinstaller "$SPEC_FILE" --upx-dir "$PKG_DIR/$UPX_VER"
