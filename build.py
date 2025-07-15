import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tarfile
import argparse

DEFAULT_UPX_VER="5.0.1"


def get_upx_compressor(build_resources: str, upx_archive: str, upx_url: str, is_windows: bool) -> str:
    """
    Checks for the presence of UPX, downloads and extracts it if not present.

    Args:
        build_resources (str): The build resources directory where UPX will be located.
        upx_archive (str): The archive name of the UPX version to download.
        upx_url (str): The URL from which to download UPX.
        is_windows (bool): True if the script is running on Windows, False otherwise.

    Returns:
        upx_dir (str): The directory where UPX is located.
    """

    upx_dir = os.path.join(build_resources, upx_archive)
    
    if not os.path.exists(upx_dir):
        print("Downloading UPX...")
        upx_path = os.path.join(build_resources, f"{upx_archive}.{'zip' if is_windows else 'tar.xz'}")
        urllib.request.urlretrieve(upx_url, upx_path)
        
        if is_windows:
            with zipfile.ZipFile(upx_path, 'r') as zip_ref:
                zip_ref.extractall(build_resources)
        else:
            with tarfile.open(upx_path, 'r:xz') as tar_ref:
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


def build_exe(spec_file: str, upx_dir: str) -> None:
    """
    Builds the psmonitor application using PyInstaller.

    Args:
        spec_file (str): The path to the PyInstaller spec file.
        upx_dir (str): The directory where UPX is located.
    """

    print("Building psmonitor...")
    subprocess.run(["pyinstaller", spec_file, "--upx-dir", upx_dir], check=True)


def main(build: str, clean_build: bool, upx_ver: str) -> None:
    """
    Main function that orchestrates the build process for psmonitor.

    Args:
        build (str): The type to build for e.g. 'gui' or 'headless'.
        clean_build (str): Clean `build` and `dist directories before build.
        upx_ver (str): The version of UPX to use to compress the executable.

    This function sets up the build environment, downloads UPX if necessary,
    cleans the build and dist directories, and then builds the application.
    """

    cwd = os.getcwd()
    build_resources = os.path.join(cwd, "build_resources")

    if os.name == 'nt':
        upx_pkg = f"upx-{upx_ver}-win64"
        upx_url = f"https://github.com/upx/upx/releases/download/v{upx_ver}/{upx_pkg}.zip"
    else:
        upx_pkg = f"upx-{upx_ver}-amd64_linux.tar"
        upx_url = f"https://github.com/upx/upx/releases/download/v{upx_ver}/{upx_pkg}.tar.xz"
    
    if clean_build:
        print("Cleaning previous build directories...")
        clean_dir(os.path.join(cwd, "build"))
        clean_dir(os.path.join(cwd, "dist"))

    upx = get_upx_compressor(build_resources, upx_pkg, upx_url, os.name == 'nt')

    build_exe(os.path.join(build_resources, build, "psmonitor.spec"), upx)

    clean_dir(upx)


if __name__ == "__main__":
    """
    Entry point of the script. Checks for command-line arguments and starts the build process.
    
    The script expects exactly one argument specifying the build target. If '--help' is provided,
    it prints the usage information.
    """

    parser = argparse.ArgumentParser(description="Build psmonitor executables.")
    parser.add_argument("build", choices=["gui", "headless"], help="Build e.g. gui or headless")
    parser.add_argument("--clean", action="store_true", help="Clean build and dist directories before building")
    parser.add_argument("--upx", metavar="VERSION", type=str, default=DEFAULT_UPX_VER, help="Specify UPX version (default: 5.0.1)")
    args = parser.parse_args()

    main(args.build, clean_build=args.clean, upx_ver=args.upx)
