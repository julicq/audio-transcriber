# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['transcriber_pyqt5ver.py'],
    pathex=['C:\\PytonCode\\audio_transcriber'],
    binaries=[],
    datas=[
        ('vosk-model-small-ru-0.22', 'vosk-model-small-ru-0.22'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transcriber_pyqt5ver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transcriber_pyqt5ver',
)
