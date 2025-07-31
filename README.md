Menu Volume
Menu Volume là một ứng dụng thanh menu trên macOS, cho phép điều chỉnh âm lượng và hiển thị biểu tượng thiết bị âm thanh (loa mặc định, AirPods, loa Bluetooth JBL/Marshall/HK) trên thanh menu.
Yêu cầu

macOS 15 trở lên
Python 3 (đã cài sẵn tại /usr/bin/python3)

Cài đặt
1. Chuẩn bị môi trường
Cài đặt các công cụ và thư viện cần thiết:
# Cài Homebrew (nếu chưa có)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Cài SwitchAudioSource
brew install switchaudio-osx

# Cài PyObjC
/usr/bin/python3 -m pip install pyobjc

2. Tải mã nguồn
Tải mã nguồn từ GitHub:
git clone https://github.com/haon2409/menu-volume.git
cd menu-volume

3. Cấu hình Launch Agent

Sao chép file com.haonguyen.menuvolume.plist vào thư mục ~/Library/LaunchAgents/:
cp com.haonguyen.menuvolume.plist ~/Library/LaunchAgents/

Nội dung file com.haonguyen.menuvolume.plist:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.haonguyen.menuvolume</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/haonguyen/Projects/menu/menu_volume/menu_volume.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/haonguyen/Projects/menu/menu_volume</string>
    <key>StandardOutPath</key>
    <string>/tmp/menuvolume.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/menuvolume.err</string>
</dict>
</plist>


Đặt quyền cho file:
chmod 644 ~/Library/LaunchAgents/com.haonguyen.menuvolume.plist



4. Chạy dịch vụ
Tải dịch vụ bằng launchctl:
launchctl load ~/Library/LaunchAgents/com.haonguyen.menuvolume.plist

Kiểm tra trạng thái:
launchctl list | grep com.haonguyen.menuvolume

5. Kiểm tra log
Xem log để đảm bảo không có lỗi:
cat /tmp/menuvolume.out
cat /tmp/menuvolume.err

Tính năng

Điều chỉnh âm lượng nhanh từ thanh menu.
Hiển thị biểu tượng tương ứng với thiết bị âm thanh (AirPods, loa Bluetooth JBL/Marshall/HK, loa mặc định).
Tích hợp với SwitchAudioSource để quản lý thiết bị âm thanh.

Gỡ lỗi

Nếu gặp lỗi ModuleNotFoundError: No module named 'AppKit', cài lại pyobjc:/usr/bin/python3 -m pip install pyobjc


Nếu gặp lỗi FileNotFoundError: /opt/homebrew/bin/SwitchAudioSource, cài lại switchaudio-osx:brew install switchaudio-osx


Đảm bảo các file icon (airpods_pro_icon.png, airpods_icon.png, bluetooth_speaker_icon.png, internal_speaker_icon.png) nằm trong thư mục /Users/haonguyen/Projects/menu/menu_volume/.

Đóng góp

Fork kho lưu trữ.
Tạo nhánh mới:git checkout -b ten-nhanh-cua-ban


Commit thay đổi:git commit -m "Mô tả thay đổi"


Đẩy lên nhánh:git push origin ten-nhanh-cua-ban


Tạo Pull Request trên GitHub.

Giấy phép
Dự án được cấp phép theo MIT License.
Liên hệ
Liên hệ qua GitHub Issues nếu có câu hỏi hoặc cần hỗ trợ.