# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

add_files = [('delta_total.png','.'),('opt1_OFF.png','.'),('opt1_ON.png','.'),('opt2_OFF.png','.'),('opt2_ON.png','.'),('opt3_OFF.png','.'),('opt3_ON.png','.'),('pause_button.png','.'),('system_logo.png','.'),('robot_icon.png','.'),('JALK3_logo_image.png','.'),('exit.png','.')]

a = Analysis(
    ['Capstone_UI.py'],
    pathex=[C:/Users/schah/바탕 화면],
    binaries=[],
    datas=add_files,
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
