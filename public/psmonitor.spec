# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['manage.py'],
        binaries=None,
        hiddenimports=[],
        hookspath=None,
        runtime_hooks=None,
        excludes=None)

a.datas += [('psmonitor.ico', 'psmonitor.ico', 'DATA')]

pyz = PYZ(a.pure)

exe = EXE(pyz,
        a.scripts,
        a.binaries,
        a.datas,
        name='psmonitor',
        strip=False,
        upx=True,
        console=True,
        icon='psmonitor.ico',
        version='version.rc')