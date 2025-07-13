# -*- mode: python ; coding: utf-8 -*-

import os


project_root = os.getcwd()
main_script = os.path.join(project_root, 'main.py')

public_folder = os.path.join(project_root, 'public')
icon_file = os.path.join(project_root, 'build_resources', 'psmonitor.ico')


block_cipher = None


a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=[],
    datas=[
        (public_folder, 'public'),
        (icon_file, 'psmonitor.ico')
    ],
    hiddenimports=[
        'PIL._tkinter_finder'
    ],
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
