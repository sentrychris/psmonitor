#!/usr/bin/env bash

UPX_VER="upx-4.2.4-amd64_linux"

PWD=$(pwd)

BUILD_DIR="$PWD/build"
DIST_DIR="$PWD/dist"

PKG_DIR="$PWD/package"
SPEC_FILE="$PKG_DIR/linux/psmonitor.spec"

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

echo "Building psmonitor for Linux..."
pyinstaller "$SPEC_FILE" --upx-dir "$PKG_DIR/$UPX_VER"