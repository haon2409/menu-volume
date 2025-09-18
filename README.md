Menu Volume - A Menu Bar Volume Control for macOS
Overview
Menu Volume is a lightweight macOS menu bar application that provides a visual volume slider, mute indicator, current output device name, and battery level for Bluetooth audio devices. It uses CoreAudio for precise control and falls back to AppleScript when needed.
Features

Visual Volume Bar: Interactive slider showing current volume level (0-100%).
Mute Detection: Changes bar color and appearance when muted.
Device Monitoring: Displays the current output device name and listens for changes.
Bluetooth Battery: Shows average battery level for connected Bluetooth headphones/speakers.
Fallback Support: Uses AppleScript if CoreAudio API fails.
Efficient Updates: Only redraws changed regions for smooth performance.

Requirements

macOS
Python 3.x
PyObjC (pip install pyobjc)
PyInstaller (pip install pyinstaller)
Xcode Command Line Tools (for compiling C code)

Installation

Clone the repository:git clone https://github.com/haon2409/menu-volume.git
cd menu-volume


Install dependencies:pip install pyobjc pyinstaller


Compile the CoreAudio library:gcc -dynamiclib -o libcoreaudio.dylib -framework CoreAudio -framework AudioToolbox -framework CoreFoundation coreaudio.c


Download SwitchAudioSource (binary for switching audio devices) and place it in the project directory.
Build the app:pyinstaller Menu\ Volume.spec


Find the built app (Menu Volume.app) in the dist folder.

File Structure

menu_volume.py: Core application logic for the menu bar volume control.
Menu Volume.spec: PyInstaller configuration for building the app.
coreaudio.c: C source code for CoreAudio integration (compile to libcoreaudio.dylib).
setup.py: Alternative build configuration using py2app.
libcoreaudio.dylib: Compiled CoreAudio library (generated during installation).
level_icon.png: Icon for the menu bar (if present).

Usage

Open dist/Menu Volume.app.
The app appears in the menu bar as a volume bar.
Drag the slider or use system volume keys to adjust volume.
Mute/unmute via system controls; the bar updates visually.
Connect Bluetooth devices to see battery levels and device names.

Notes

Ensure SwitchAudioSource is downloaded from GitHub and placed in the project root.
The app suppresses C library logs by redirecting stdout.
Battery level parsing works for standard Bluetooth audio devices via system_profiler.
For py2app builds, run python setup.py py2app instead of PyInstaller.

Troubleshooting

Volume not updating: Check if libcoreaudio.dylib is compiled correctly; verify CoreAudio permissions.
Device not detected: Ensure SwitchAudioSource is executable (chmod +x SwitchAudioSource).
Build errors: Install Xcode tools (xcode-select --install) for gcc.
Battery level missing: Run system_profiler SPBluetoothDataType manually to test Bluetooth detection.

License
MIT License. See LICENSE for details.