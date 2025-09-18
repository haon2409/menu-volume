Menu Volume
Menu Volume is a lightweight macOS menu bar application that provides a visual volume slider, mute indicator, current output device name, and battery level for Bluetooth audio devices. It uses CoreAudio for precise control and falls back to AppleScript when needed.
Features

Visual Volume Bar: Interactive slider showing current volume level (0-100%).
Mute Detection: Changes bar color and appearance when muted.
Device Monitoring: Displays the current output device name and listens for changes.
Bluetooth Battery: Shows average battery level for connected Bluetooth headphones/speakers.
Fallback Support: Uses AppleScript if CoreAudio API fails.
Efficient Updates: Only redraws changed regions for smooth performance.

System Requirements

macOS 10.15 or later
No Python or dependencies required for the standalone app

Installation

Download the App:
Download Menu Volume.app from the Releases page or build from source.


Install the App:
Copy Menu Volume.app to /Applications/:cp -r "Menu Volume.app" /Applications/




Run the App:
Double-click Menu Volume.app in Finder, or use:open /Applications/"Menu Volume.app"





Usage

Adjust Volume: Click and drag the slider in the menu bar to increase/decrease volume.
View Device Info: The icon on the slider indicates the current audio device (AirPods, Bluetooth speakers, or internal speakers).
Check Battery: For Bluetooth devices, the slider shows battery level (red if <20%, green if >20%).
Quit: Right-click the slider and select Quit.

Project Structure
menu-volume/
├── assets/
│   ├── airpods_icon.png
│   ├── airpods_pro_icon.png
│   ├── bluetooth_speaker_icon.png
│   ├── internal_speaker_icon.png
│   └── app.icns
├── Menu Volume.app          # Built standalone app
├── Menu Volume.spec         # PyInstaller config
├── MyIcon.iconset           # Source for app icon
├── README.md
├── SwitchAudioSource        # Binary for device switching
├── build_volume.sh          # Build script
├── coreaudio.c              # CoreAudio C source
├── libcoreaudio.dylib       # Compiled CoreAudio library
├── menu_volume.py           # Main Python script
└── setup.py                 # py2app config

Building from Source

Prerequisites:
Install Python 3 and dependencies:pip3 install pyobjc pyinstaller


Install Xcode Command Line Tools:xcode-select --install


Download SwitchAudioSource and place it in the project root.


Compile CoreAudio Library:gcc -dynamiclib -o libcoreaudio.dylib -framework CoreAudio -framework AudioToolbox -framework CoreFoundation coreaudio.c


Build the App:
Using the script:./build_volume.sh


Or manually:pyinstaller "Menu Volume.spec"


Alternative with py2app:python3 setup.py py2app




Output:
The standalone Menu Volume.app will be in the project root or dist/ folder.



Developer Notes

App Icon: Generated from MyIcon.iconset using:iconutil -c icns MyIcon.iconset -o assets/app.icns


Icons: PNG files in assets/ are used for device-specific icons.
Debugging: For build errors, run with debug logs:pyinstaller --clean --log-level=DEBUG "Menu Volume.spec"


Troubleshooting:
Volume not updating: Verify libcoreaudio.dylib compilation and CoreAudio permissions.
Device detection issues: Ensure SwitchAudioSource is executable (chmod +x SwitchAudioSource).
Battery info missing: Test with system_profiler SPBluetoothDataType.



License
This project is licensed under the MIT License. See LICENSE for details.
Contact
For questions or contributions, open an issue on this repository or contact the author at haon2409@example.com.