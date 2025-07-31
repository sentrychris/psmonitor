"""
Build script for PSMonitor application.

This script automates the process of downloading UPX (if needed),
cleaning previous build artifacts, and building the PSMonitor
executable for the specified build type (GUI or headless).

Usage:
    python build.py [gui|headless] [--clean] [--upx VERSION]

Arguments:
    --build TYPE            Specify the build type: "gui" or "headless"
    --clean                 Delete previous build and dist directories before building
    --upx VERSION           Specify the UPX version to download and use (default: 5.0.1)
    --upx-clean             Delete the UPX directory in build_resources after building
    --insert-docstrings     Insert docstrings into .py source files (does not build EXEs)
    --third-party-licenses  Generate third-party licenses file (does not build EXEs)

The script handles platform differences for UPX download URLs and extraction.
"""

import os
import shutil
import subprocess
import urllib.request
import zipfile
import tarfile
import argparse

from build_resources.generate_docstrings import insert_docstrings
from build_resources.generate_third_party_licenses import generate_third_party_licenses

DEFAULT_UPX_VER="5.0.1"


def get_upx(build_resources: str, upx_pkg: str, upx_url: str, is_windows: bool) -> str:
    """
    Checks for the presence of UPX, downloads and extracts it if not present.

    Args:
        build_resources (str): The build resources directory where UPX will be located.
        upx_pkg (str): The archive name of the UPX version to download.
        upx_url (str): The URL from which to download UPX.
        is_windows (bool): True if the script is running on Windows, False otherwise.

    Returns:
        upx_dir (str): The directory where UPX is located.
    """

    upx_dir = os.path.join(build_resources, upx_pkg)

    if not os.path.exists(upx_dir):
        print("Downloading UPX...")
        upx_path = os.path.join(build_resources, f"{upx_pkg}.{'zip' if is_windows else 'tar.xz'}")
        urllib.request.urlretrieve(upx_url, upx_path)

        if is_windows:
            with zipfile.ZipFile(upx_path, "r") as zip_ref:
                zip_ref.extractall(build_resources)
        else:
            with tarfile.open(upx_path, "r:xz") as tar_ref:
                tar_ref.extractall(build_resources)

        os.remove(upx_path)
    else:
        print("UPX is available")

    return upx_dir


def clean_dir(directory: str) -> None:
    """
    Deletes the specified directory and all its contents if it exists.

    Args:
        directory (str): The directory to be cleaned.
    """

    if os.path.exists(directory):
        print(f"Cleaning {directory} directory...")
        shutil.rmtree(directory)


def build_exe(spec_file: str, upx_dir: str, dist_dir: str, build_dir: str) -> None:
    """
    Builds the PSMonitor application using PyInstaller.

    Args:
        spec_file (str): The path to the PyInstaller spec file.
        upx_dir (str): The directory where UPX is located.
        dist_dir (str): Output directory for final executable.
        build_dir (str): Directory for PyInstaller's build artifacts.
    """

    print("Building PSMonitor...")
    subprocess.run([
        "pyinstaller",
        spec_file,
        "--upx-dir", upx_dir,
        "--distpath", dist_dir,
        "--workpath", build_dir
    ], check=True)


def main(
        build_type: str,
        clean_build: bool,
        clean_upx: bool,
        upx_ver: str,
        insert_docstrings_only: bool = False,
        third_party_licenses_only: bool = False
    ) -> None:
    """
    Main function that orchestrates the build process for PSMonitor.

    Args:
        build (str): The type to build for e.g. "gui" or "headless".
        clean_build (bool): Clean `build` and `dist` directories before build.
        clean_upx (bool): Delete the UPX directory after building
        upx_ver (str): The version of UPX to use to compress the executable.
        insert_docstrings_only (bool): Insert docstrings into source files instead.
        third_party_licenses_only (bool): Generate third-party licenses instead.
    """
    root = os.path.dirname(__file__)
    out_dir = os.path.join(root, "output")
    dist_dir = os.path.join(out_dir, "dist")
    build_dir = os.path.join(out_dir, "build")

    # Handle insert docstrings only (no build)
    if insert_docstrings_only:
        print("Inserting docstrings into source .py files...")
        insert_docstrings()
        return

    # Handle generating licenses only (no build)
    if third_party_licenses_only:
        print("Generating third-party licenses file...")
        generate_third_party_licenses()
        return

    # Handle clean previous builds only (no build)
    if clean_build and not build_type:
        print("Cleaning previous build directories...")
        clean_dir(out_dir)
        return

    # Right... Now we're building... Make sure the build type is valid
    if build_type not in ["gui", "headless"]:
        raise ValueError("Invalid build type. Must be: `gui` or `headless`.")

    build_resources = os.path.join(root, "build_resources")
    build_spec = os.path.join(build_resources, build_type, "psmonitor.spec")

    if not os.path.exists(build_spec):
        raise FileNotFoundError(f".spec file not found: {build_spec}")

    # Handle clean previous builds before new build
    if clean_build:
        print("Cleaning previous build directories...")
        clean_dir(out_dir)

    # Handle fetching UPX
    if os.name == "nt":
        upx_pkg = f"upx-{upx_ver}-win64"
        upx_url = f"https://github.com/upx/upx/releases/download/v{upx_ver}/{upx_pkg}.zip"
    else:
        upx_pkg = f"upx-{upx_ver}-amd64_linux"
        upx_url = f"https://github.com/upx/upx/releases/download/v{upx_ver}/{upx_pkg}.tar.xz"
    upx_dir = get_upx(build_resources, upx_pkg, upx_url, os.name == "nt")

    build_exe(
        spec_file=build_spec,
        upx_dir=upx_dir,
        dist_dir=os.path.join(dist_dir, build_type),
        build_dir=os.path.join(build_dir, build_type)
    )

    if clean_upx:
        clean_dir(upx_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PSMonitor build utilities.")

    parser.add_argument(
        "--build",
        choices=["gui", "headless"],
        help="Build type (gui or headless)"
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build and dist directories before building"
    )

    parser.add_argument(
        "--upx",
        metavar="VERSION",
        type=str,
        default=DEFAULT_UPX_VER,
        help="Specify UPX version (default: 5.0.1)"
    )

    parser.add_argument(
        "--upx-clean",
        action="store_true",
        help="Clean copy of UPX before building"
    )

    parser.add_argument(
        "--insert-docstrings",
        action="store_true",
        help="Insert docstrings into source files instead of building"
    )

    parser.add_argument(
        "--third-party-licenses",
        action="store_true",
        help="Generate third-party licenses file instead of building"
    )

    args = parser.parse_args()

    main(
        build_type=args.build,
        clean_build=args.clean,
        clean_upx=args.upx_clean,
        upx_ver=args.upx,
        insert_docstrings_only=args.insert_docstrings,
        third_party_licenses_only=args.third_party_licenses
    )
