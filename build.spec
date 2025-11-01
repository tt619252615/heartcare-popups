# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
使用方法: pyinstaller build.spec
"""

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),           # 包含配置文件
        ('data/messages.txt', 'data'),  # 包含消息文件
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'numpy',
        'pydantic',
        'pydantic_core',
        'loguru',
        'keyboard',  # 全局键盘监听库
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
    name='HeartCarePopups',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口（如需调试改为True）
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径，如 'assets/icon.ico'
    uac_admin=True,  # 请求管理员权限（ESC键监听需要）
)
