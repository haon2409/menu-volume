#!/usr/bin/env python3
from setuptools import setup
import glob
import os

# Lấy tất cả file hình ảnh (.png) trong thư mục hiện tại
image_files = glob.glob('*.png')

# Danh sách tài nguyên cần đóng gói
DATA_FILES = [
    ('', ['libcoreaudio.dylib', 'SwitchAudioSource'] + image_files),
]

OPTIONS = {
    'argv_emulation': False,  # Tắt argv_emulation để tránh lỗi Carbon
    'plist': {
        'CFBundleName': 'MenuVolumeBar',
        'CFBundleDisplayName': 'MenuVolumeBar',
        'CFBundleGetInfoString': 'Volume control bar for macOS menu bar',
        'CFBundleIdentifier': 'com.example.menuvolumebar',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025, Your Name',
        'LSUIElement': True,
        'NSPrincipalClass': 'NSApplication',
    },
    'packages': ['AppKit', 'objc', 'ctypes', 'subprocess'],
    'optimize': 2,
    'iconfile': 'app.icns' if os.path.exists('app.icns') else None,
}

setup(
    app=['menu_volume.py'],
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)