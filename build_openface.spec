# -*- mode: python ; coding: utf-8 -*-

import sys
import os

sys.setrecursionlimit(20000)

block_cipher = None

venv_root_path = sys.prefix
print("venv_root_path:", venv_root_path)

a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
('.\\Resources', 'Resources'),
('shape_predictor_68_face_landmarks.dat', '.'),
('.\\Data', 'Data'),
('.\\AU_predictors', 'AU_predictors'),
('.\\compiled_libraries', 'compiled_libraries'),
('.\\model', 'model'),
('au_intensities.csv', '.'),
('targets.csv', '.'),
('haarcascade_frontalface_alt.xml', '.'),
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
    [('u', None, 'OPTION')],
    exclude_binaries=True,
    name='main_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main_gui',
)
