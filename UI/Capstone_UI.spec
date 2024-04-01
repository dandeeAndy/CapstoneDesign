# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['Capstone_UI.py'],
    pathex=[],
    binaries=[],
    datas = [
        ('exit.png'),
        ('fragile_OFF.png'),
        ('fragile_ON.png'),
        ('Rectangle.png'),
        ('robot_icon.png'),
        ('system_logo.png'),
        ('transport_OFF.png'),
        ('transport_ON.png'),
        ('courier_OFF.png'),
        ('courier_ON.png'),
        ('assembly_image,jpg')
    ],
    hiddenimports=['PyQt5.QtWidgets.*',
        'PyQt5.QtCore.*',
        'PyQt5.QtGui.*'],
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
    name='Capstone_UI',
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
