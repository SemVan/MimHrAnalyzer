# -*- mode: python ; coding: utf-8 -*-

import sys
import os

sys.setrecursionlimit(20000)

block_cipher = None

def get_mediapipe_path():
    import mediapipe
    mediapipe_path = mediapipe.__path__[0]
    return mediapipe_path

venv_root_path = sys.prefix
print("venv_root_path:", venv_root_path)

a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[

('.\\Resources', 'Resources'),
('LibreFace_AU_Encoder.onnx', '.'),
('LibreFace_AU_Intensity.onnx', '.'),
('LibreFace_AU_Presence.onnx', '.'),
('LibreFace_FE.onnx', '.'),
('shape_predictor_68_face_landmarks.dat', '.'),
(os.path.join(venv_root_path, 'Lib\\site-packages\\onnxruntime\\capi\onnxruntime_providers_shared.dll'),'onnxruntime\\capi'),
('.\\Data', 'Data'),
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

mediapipe_tree = Tree(get_mediapipe_path(), prefix='mediapipe', excludes=["*.pyc"])
a.datas += mediapipe_tree
a.binaries = filter(lambda x: 'mediapipe' not in x[0], a.binaries)

excludes = [
'mediapipe\\modules\\hand_landmark',
'mediapipe\\modules\\holistic_landmark',
'mediapipe\\modules\\palm_detection',
'mediapipe\\modules\\pose_detection',
'mediapipe\\modules\\pose_landmark'
]
datas = []
for d in a.datas:
    skip=False
    for e in excludes:
        if e in d[0]:
            skip=True
            break
    if not skip: datas.append(d)
a.datas = TOC(datas)

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
