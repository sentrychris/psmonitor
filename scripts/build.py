import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tarfile


def print_usage():
    """
    Prints the usage information for the script and exits.

    This function provides instructions on how to use the script, including
    the available build types and an example of how to run the script.
    """

    print("Usage: Build binary executables for PSMonitor.\n")
    print("Example:")
    print("  python build.py <build-type>\n")
    print("Available build types (at least one is required):")
    print("  - desktop : Build the desktop application with the server included.")
    print("  - server  : Build the standalone server only.\n")
    sys.exit(1)


def prepare_upx(pkg_dir: str, upx_ver: str, upx_url: str, is_windows: bool) -> str:
    """
    Checks for the presence of UPX, downloads and extracts it if not present.

    Args:
        pkg_dir (str): The directory where the UPX package should be located.
        upx_ver (str): The version of UPX to check/download.
        upx_url (str): The URL from which to download the UPX package.
        is_windows (bool): True if the script is running on Windows, False otherwise.

    Returns:
        upx_dir (str): The directory where the UPX package is located.
    """

    upx_dir = os.path.join(pkg_dir, upx_ver)
    
    if not os.path.exists(upx_dir):
        print("Downloading UPX...")
        upx_path = os.path.join(pkg_dir, f"{upx_ver}.{'zip' if is_windows else 'tar.xz'}")
        urllib.request.urlretrieve(upx_url, upx_path)
        
        if is_windows:
            with zipfile.ZipFile(upx_path, 'r') as zip_ref:
                zip_ref.extractall(pkg_dir)
        else:
            with tarfile.open(upx_path, 'r:xz') as tar_ref:
                tar_ref.extractall(pkg_dir)
                
        os.remove(upx_path)
    else:
        print("UPX is available")

    return upx_dir


def clean_directory(directory: str):
    """
    Deletes the specified directory and all its contents if it exists.

    Args:
        directory (str): The directory to be cleaned.
    """

    if os.path.exists(directory):
        print(f"Cleaning {directory} directory...")
        shutil.rmtree(directory)


def build_psmonitor(spec_file: str, upx_dir: str):
    """
    Builds the PSMonitor application using PyInstaller.

    Args:
        spec_file (str): The path to the PyInstaller spec file.
        upx_dir (str): The directory where UPX is located.
    """

    print("Building psmonitor...")
    subprocess.run(["pyinstaller", spec_file, "--upx-dir", upx_dir], check=True)


def main(build_type: str):
    """
    Main function that orchestrates the build process for PSMonitor.

    Args:
        build_type (str): The type of build to perform ('desktop' or 'server').

    This function sets up the build environment, downloads UPX if necessary,
    cleans the build and dist directories, and then builds the application.
    """

    if build_type not in ["desktop", "server"]:
        print_usage()

    build_spec = "psmonitor_server.spec" if build_type == "server" else "psmonitor.spec"
    pwd = os.getcwd()
    build_dir = os.path.join(pwd, "build")
    dist_dir = os.path.join(pwd, "dist")
    pkg_dir = os.path.join(pwd, "package")
    spec_file = os.path.join(pkg_dir, build_type, "windows" if os.name == 'nt' else "linux", build_spec)

    if os.name == 'nt':
        upx_ver = "upx-4.2.4-win64"
        upx_url = f"https://github.com/upx/upx/releases/download/v4.2.4/{upx_ver}.zip"
    else:
        upx_ver = "upx-4.2.4-amd64_linux"
        upx_url = f"https://github.com/upx/upx/releases/download/v4.2.4/{upx_ver}.tar.xz"

    print("Preparing UPX...")
    upx_dir = prepare_upx(pkg_dir, upx_ver, upx_url, os.name == 'nt')
    
    clean_directory(build_dir)
    clean_directory(dist_dir)

    build_psmonitor(spec_file, os.path.join(pkg_dir, upx_ver))

    print("Cleaning UPX...")
    clean_directory(upx_dir)


if __name__ == "__main__":
    """
    Entry point of the script. Checks for command-line arguments and starts the build process.
    
    The script expects exactly one argument specifying the build type. If '--help' is provided,
    it prints the usage information.
    """

    if len(sys.argv) != 2 or sys.argv[1] == '--help':
        print_usage()
    main(sys.argv[1])
