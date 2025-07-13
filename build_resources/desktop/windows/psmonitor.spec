# -*- mode: python ; coding: utf-8 -*-

import os


project_root = os.path.join(os.getcwd(), 'src')
main_script = os.path.join(project_root, 'main.py')
ui_folder = os.path.join(project_root, 'ui')

libwincputemp = os.path.join(os.getcwd(), 'bin', 'libwincputemp.exe')
icon_file = os.path.join(os.getcwd(), 'build_resources', 'psmonitor.ico')
version_file = os.path.join(os.getcwd(), 'build_resources', 'desktop', 'windows', 'version.rc')


block_cipher = None


a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=[],
    datas=[
        (libwincputemp, '.'),
        (ui_folder, 'ui'),
        (icon_file, 'psmonitor.ico'),
        (version_file, 'version.rc')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='psmonitor',
    icon=icon_file,
    version=version_file,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
