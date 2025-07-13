import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tarfile


UPX_VER="5.0.1"


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


def clean_dir(directory: str):
    """
    Deletes the specified directory and all its contents if it exists.

    Args:
        directory (str): The directory to be cleaned.
    """

    if os.path.exists(directory):
        print(f"Cleaning {directory} directory...")
        shutil.rmtree(directory)


def build(spec_file: str, upx_dir: str):
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

    cwd = os.getcwd()
    build_resources = os.path.join(cwd, "build_resources")
    build_spec = "psmonitor_server.spec" if build_type == "server" else "psmonitor.spec"
    spec_file = os.path.join(build_resources, build_type, "windows" if os.name == 'nt' else "linux", build_spec)

    if os.name == 'nt':
        upx_pkg = f"upx-{UPX_VER}-win64"
        upx_url = f"https://github.com/upx/upx/releases/download/v{UPX_VER}/{upx_pkg}.zip"
    else:
        upx_pkg = f"upx-{UPX_VER}-amd64_linux.tar"
        upx_url = f"https://github.com/upx/upx/releases/download/v{UPX_VER}/{upx_pkg}.tar.xz"

    print("Preparing UPX...")
    upx_compressor = get_upx_compressor(build_resources, upx_pkg, upx_url, os.name == 'nt')
    
    clean_dir(os.path.join(cwd, "build"))
    clean_dir(os.path.join(cwd, "dist"))

    build(spec_file, upx_compressor)

    print("Cleaning UPX...")
    clean_dir(upx_compressor)


if __name__ == "__main__":
    """
    Entry point of the script. Checks for command-line arguments and starts the build process.
    
    The script expects exactly one argument specifying the build type. If '--help' is provided,
    it prints the usage information.
    """

    if len(sys.argv) != 2 or sys.argv[1] == '--help':
        print_usage()
    main(sys.argv[1])
