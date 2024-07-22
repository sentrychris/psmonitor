#!/usr/bin/env bash

UPX_RELEASE="upx-4.2.1-win64"
SPEC_FILE="psmonitor.spec"

CWD=$(pwd)

if [ ! -f "$CWD/$SPEC_FILE" ]; then
  echo "This script must be run from the same directory containing $SPEC_FILE"
  exit 1
fi

BUILD_DIR="./build"
DIST_DIR="./dist"

echo "Building $SPEC_FILE..."

# Check for UPX
echo "Checking for UPX..."
if [ ! -d "./$UPX_RELEASE" ]; then
  echo "Downloading UPX"
  curl -LO "https://github.com/upx/upx/releases/download/v4.2.1/$UPX_RELEASE.zip"
  unzip "./$UPX_RELEASE.zip" -d ./
  rm -f "./$UPX_RELEASE.zip"
else
  echo "UPX is available"
fi

# Check build dir
if [ -d $BUILD_DIR ]; then
  echo "Cleaning build directory..."
  rm -rf $BUILD_DIR
fi

# Check dist dir
if [ -d $DIST_DIR ]; then
  echo "Cleaning dist directory..."
  rm -rf $DIST_DIR
fi

pyinstaller $SPEC_FILE --upx-dir "./$UPX_RELEASE"

echo "Removing UPX"
rm -rf "./$UPX_RELEASE"