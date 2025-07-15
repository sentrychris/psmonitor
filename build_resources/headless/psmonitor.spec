# -*- mode: python ; coding: utf-8 -*-
import os
import sys

cwd = os.getcwd()
project_root = os.path.join(cwd, 'src')
headless_script = os.path.join(project_root, 'headless.py')
gui_folder = os.path.join(project_root, 'gui')
icon_file = os.path.join(cwd, 'build_resources', 'psmonitor.ico')
libwincputemp = os.path.join(cwd, 'bin', 'libwincputemp.exe') if sys.platform == 'win32' else None
version_file = os.path.join(cwd, 'build_resources', 'shared', 'windows', 'version.rc') if sys.platform == 'win32' else None

datas = [(gui_folder, 'gui'), (icon_file, 'psmonitor.ico')]
if sys.platform == 'win32':
    datas += [(libwincputemp, '.'), (version_file, 'version.rc')]

block_cipher = None

a = Analysis(
    [headless_script],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='psmonitor-headless',
    icon=icon_file if sys.platform == 'win32' else None,
    version=version_file if sys.platform == 'win32' else None,
    console=True,
    debug=False,
    upx=True,
)