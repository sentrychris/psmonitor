import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tarfile


def check_and_download_upx(pkg_dir, upx_ver, upx_url, is_windows):
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


def clean_directory(directory):
    if os.path.exists(directory):
        print(f"Cleaning {directory} directory...")
        shutil.rmtree(directory)


def build_psmonitor(spec_file, upx_dir):
    print("Building psmonitor...")
    subprocess.run(["pyinstaller", spec_file, "--upx-dir", upx_dir], check=True)


def main(build_type):
    if build_type not in ["desktop", "server"]:
        print("Usage: Build executables for psmonitor.\n")
        print("Example:")
        print("  python build_script.py <build-type>\n")
        print("Available build types (at least one is required):")
        print("  - desktop : Build the desktop application with the server included.")
        print("  - server  : Build the standalone server only.\n")
        sys.exit(1)

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

    print("Checking for UPX...")
    check_and_download_upx(pkg_dir, upx_ver, upx_url, os.name == 'nt')
    
    clean_directory(build_dir)
    clean_directory(dist_dir)

    build_psmonitor(spec_file, os.path.join(pkg_dir, upx_ver))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python build_script.py <build-type>")
        sys.exit(1)
    main(sys.argv[1])
