import os
import AppKit
import objc
import ctypes
import sys
import subprocess

# Tải thư viện Core Audio
coreaudio_lib = ctypes.cdll.LoadLibrary("./libcoreaudio.dylib")
coreaudio_lib.getSystemVolume.restype = ctypes.c_float
coreaudio_lib.getSystemMuted.restype = ctypes.c_int
coreaudio_lib.setSystemVolume.argtypes = [ctypes.c_float]
coreaudio_lib.getCurrentOutputDevice.restype = ctypes.c_char_p

# Định nghĩa kiểu callback
CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
coreaudio_lib.registerDeviceListener.argtypes = [CALLBACK]
coreaudio_lib.registerDeviceListener.restype = None

# Chuyển hướng stdout để tránh log từ C
class PythonOutput:
    def write(self, text):
        pass
    def flush(self):
        pass
sys.stdout = PythonOutput()

class VolumeBarView(AppKit.NSView):
    def initWithFrame_(self, frame):
        self = objc.super(VolumeBarView, self).initWithFrame_(frame)
        if self:
            self.volume = 0
            self.onVolumeChanged = None
            self.circle_radius = 3
            frame.size.height = self.circle_radius
            self.is_muted = False
            self.current_center_x = 0
            self.current_center_y = 0
            self.last_center_x = 0
            self.current_device = "Unknown"
            self.battery_level = None  # Giữ thuộc tính này để tương thích
        return self

    def setVolume_(self, volume):
        self.last_center_x = self.current_center_x
        self.volume = volume
        self.updateDisplayRegion()

    def setMuted_(self, muted):
        self.is_muted = muted
        self.setNeedsDisplay_(True)

    def setDevice_(self, device_name):
        self.current_device = device_name
        self.setNeedsDisplay_(True)

    def setBatteryLevel_(self, battery_level):
        self.battery_level = battery_level
        self.setNeedsDisplay_(True)

    def setOnVolumeChanged_(self, callback):
        self.onVolumeChanged = callback

    def updateDisplayRegion(self):
        width = self.bounds().size.width
        height = self.bounds().size.height
        self.circle_radius = height
        radius = self.circle_radius / 2
        circle_center_x = (self.volume / 100.0) * width
        circle_center_x_display = max(radius, min(width - radius, circle_center_x))
        self.current_center_x = circle_center_x_display
        self.current_center_y = height / 2
        padding = self.circle_radius * 0.5
        min_x = min(self.last_center_x, self.current_center_x) - self.circle_radius - padding
        max_x = max(self.last_center_x, self.current_center_x) + self.circle_radius + padding
        region_width = max_x - min_x
        region_rect = AppKit.NSRect(AppKit.NSPoint(min_x, 0), AppKit.NSSize(region_width, height))
        self.setNeedsDisplayInRect_(region_rect)

    def drawRect_(self, rect):
        width = self.bounds().size.width
        height = self.bounds().size.height
        self.circle_radius = height
        radius = self.circle_radius / 2

        circle_center_x = (self.volume / 100.0) * width
        circle_center_x_display = max(radius, min(width - radius, circle_center_x))
        circle_center_y = height / 2
        self.current_center_x = circle_center_x_display
        self.current_center_y = circle_center_y

        fill_width = circle_center_x_display + radius
        fill_width = max(self.circle_radius, min(width, fill_width))

        # Vẽ nền thanh trượt
        if self.is_muted:
            background_color = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.3, 0.3, 1.0)
        else:
            background_color = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.5, 0.5, 1.0)
        background_color.setFill()
        background_path = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            AppKit.NSRect(AppKit.NSPoint(0, 0), AppKit.NSSize(width, height)), radius, radius
        )
        background_path.fill()

        # Vẽ phần đã điền
        if self.is_muted:
            fill_color = AppKit.NSColor.whiteColor().colorWithAlphaComponent_(0.5)
        else:
            fill_color = AppKit.NSColor.whiteColor().colorWithAlphaComponent_(0.8)
        fill_color.setFill()
        fill_path = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            AppKit.NSRect(AppKit.NSPoint(0, 0), AppKit.NSSize(fill_width, height)), radius, radius
        )
        fill_path.fill()

        # Vẽ bóng cho nút tròn
        AppKit.NSGraphicsContext.currentContext().saveGraphicsState()
        shadow = AppKit.NSShadow.alloc().init()
        shadow.setShadowOffset_(AppKit.NSSize(0, -1))
        shadow.setShadowBlurRadius_(2)
        shadow.setShadowColor_(AppKit.NSColor.blackColor().colorWithAlphaComponent_(0.2))
        shadow.set()
        circle_path = AppKit.NSBezierPath.bezierPathWithOvalInRect_(
            AppKit.NSRect(
                AppKit.NSPoint(circle_center_x_display - self.circle_radius / 2, circle_center_y - self.circle_radius / 2),
                AppKit.NSSize(self.circle_radius, self.circle_radius)
            )
        )
        if self.is_muted or self.volume == 0:
            gradient = AppKit.NSGradient.alloc().initWithStartingColor_endingColor_(
                AppKit.NSColor.lightGrayColor(),
                AppKit.NSColor.lightGrayColor().colorWithAlphaComponent_(0.6)
            )
        else:
            gradient = AppKit.NSGradient.alloc().initWithStartingColor_endingColor_(
                AppKit.NSColor.whiteColor().colorWithAlphaComponent_(0.8),
                AppKit.NSColor.whiteColor().colorWithAlphaComponent_(0.6)
            )
        gradient.drawInBezierPath_relativeCenterPosition_(circle_path, AppKit.NSPoint(0, 0))

        # Vẽ lớp pin (nếu có)
        if self.battery_level is not None and self.battery_level > 0:
            AppKit.NSGraphicsContext.currentContext().saveGraphicsState()
            circle_path.addClip()
            if self.battery_level < 20:
                battery_fill_color = AppKit.NSColor.systemRedColor().colorWithAlphaComponent_(0.9)
            else:
                battery_fill_color = AppKit.NSColor.systemGreenColor().colorWithAlphaComponent_(0.9)                
            
            battery_fill_color.setFill()
            fill_height = self.circle_radius * (self.battery_level / 100.0)
            battery_rect = AppKit.NSRect(
                AppKit.NSPoint(circle_center_x_display - self.circle_radius / 2, circle_center_y - self.circle_radius / 2),
                AppKit.NSSize(self.circle_radius, fill_height)
            )
            AppKit.NSBezierPath.bezierPathWithRect_(battery_rect).fill()
            AppKit.NSGraphicsContext.currentContext().restoreGraphicsState()

        # Viền đen
        border_color = AppKit.NSColor.blackColor().colorWithAlphaComponent_(0.3)
        border_color.setStroke()
        circle_path.setLineWidth_(0.5)
        circle_path.stroke()
        AppKit.NSGraphicsContext.currentContext().restoreGraphicsState()

        # Vẽ biểu tượng loa
        self.drawSpeakerIcon_(None)

    def drawSpeakerIcon_(self, _):
        center_x = self.current_center_x
        center_y = self.current_center_y
        device_name = self.current_device.lower()
        if "airpods pro" in device_name:
            icon_path = "airpods_pro_icon.png"
        elif "airpods" in device_name:
            icon_path = "airpods_icon.png"
        elif any(brand in device_name for brand in ["jbl", "marshall", "hk"]):
            icon_path = "bluetooth_speaker_icon.png"
        elif "macbook" in device_name or "speakers" in device_name:
            icon_path = "internal_speaker_icon.png"
        else:
            icon_path = "internal_speaker_icon.png"
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(icon_path)
        if not image:
            image = AppKit.NSImage.alloc().initWithContentsOfFile_("internal_speaker_icon.png")
        if image:
            image_size = self.circle_radius * 0.8
            image.drawInRect_fromRect_operation_fraction_(
                AppKit.NSRect(AppKit.NSPoint(center_x - image_size / 2, center_y - image_size / 2), AppKit.NSSize(image_size, image_size)),
                AppKit.NSRect(AppKit.NSPoint(0, 0), image.size()),
                AppKit.NSCompositeSourceOver,
                1.0
            )

    def mouseDown_(self, event):
        self.updateVolumeFromMouseEvent_(event)

    def mouseDragged_(self, event):
        self.updateVolumeFromMouseEvent_(event)

    def updateVolumeFromMouseEvent_(self, event):
        mouse_location = self.convertPoint_fromView_(event.locationInWindow(), None)
        width = self.bounds().size.width
        adjusted_mouse_x = max(0, min(width, mouse_location.x))
        threshold = width * 0.1
        if adjusted_mouse_x <= threshold:
            new_volume = 0
        elif adjusted_mouse_x >= (width - threshold):
            new_volume = 100
        else:
            new_volume = (adjusted_mouse_x / width) * 100
            new_volume = max(0, min(100, new_volume))
        self.setVolume_(new_volume)
        if self.onVolumeChanged:
            self.onVolumeChanged(new_volume)

class MenuVolumeBarApp:
    def __init__(self):
        self.app = AppKit.NSApplication.sharedApplication()
        self.status_bar = AppKit.NSStatusBar.systemStatusBar()
        self.status_item = self.status_bar.statusItemWithLength_(AppKit.NSVariableStatusItemLength)
        self.set_up_menu_bar_only()
        self.last_volume = None
        self.last_muted = None
        self.last_device = None
        self.use_fallback = False

        self.volume_view = VolumeBarView.alloc().initWithFrame_(AppKit.NSRect(AppKit.NSPoint(0, 0), AppKit.NSSize(90, 3)))
        self.volume_view.setOnVolumeChanged_(self.on_volume_changed)
        self.status_item.setView_(self.volume_view)

        # Đăng ký callback thay đổi thiết bị
        @CALLBACK
        def on_device_changed(device_name):
            device_name_str = device_name.decode('utf-8')
            print(f"Device changed to: {device_name_str}")
            self.volume_view.setDevice_(device_name_str)
            self.last_device = device_name_str
            self.update_battery_level()  # Cập nhật mức pin khi thiết bị thay đổi

        coreaudio_lib.registerDeviceListener(on_device_changed)

        # Khởi tạo thiết bị ban đầu
        initial_device = coreaudio_lib.getCurrentOutputDevice().decode('utf-8')
        self.volume_view.setDevice_(initial_device)
        self.last_device = initial_device

        self.update_volume()
        self.update_battery_level()  # Cập nhật mức pin ban đầu

        # Timer cho âm lượng (0.5 giây)
        self.volume_timer = AppKit.NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.5, self, objc.selector(self.check_volume, signature=b'v@:'), None, True
        )
        # Timer cho mức pin (1 phút = 60 giây)
        self.battery_timer = AppKit.NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            60, self, objc.selector(self.update_battery_level, signature=b'v@:'), None, True
        )
        self.app.run()

    def set_up_menu_bar_only(self):
        self.app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)

    def get_volume(self):
        volume = coreaudio_lib.getSystemVolume()
        if volume < 0:
            self.use_fallback = True
            script = 'output volume of (get volume settings)'
            process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                volume = 0.0
            else:
                try:
                    volume = int(output.strip())
                except ValueError:
                    volume = 0.0
        else:
            self.use_fallback = False
        return volume

    def get_muted(self):
        muted = coreaudio_lib.getSystemMuted()
        if muted == -1 and self.use_fallback:
            script = 'output muted of (get volume settings)'
            process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                muted = False
            else:
                muted = output.strip().lower() == b'true'
        return muted

    def set_volume(self, volume):
        if 0 <= volume <= 100:
            if self.use_fallback:
                script = f'set volume output volume {int(volume)}'
                subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            else:
                coreaudio_lib.setSystemVolume(ctypes.c_float(volume))

    def on_volume_changed(self, new_volume):
        self.set_volume(new_volume)
        self.last_volume = new_volume

    def update_volume(self):
        current_volume = self.get_volume()
        current_muted = self.get_muted()
        if current_volume != self.last_volume or current_muted != self.last_muted:
            self.last_volume = current_volume
            self.last_muted = current_muted
            self.volume_view.setMuted_(current_muted)
            self.volume_view.setVolume_(current_volume)

    def check_volume(self):
        self.update_volume()

    def update_battery_level(self):
        try:            
            current_output = subprocess.check_output(["/opt/homebrew/bin/SwitchAudioSource", "-c"], text=True).strip()
            if not current_output:
                self.volume_view.setBatteryLevel_(None)
                return
            output = subprocess.check_output(["system_profiler", "SPBluetoothDataType"], text=True)
            battery_level = self.parse_battery_level(output, current_output)
            self.volume_view.setBatteryLevel_(battery_level)
        except subprocess.CalledProcessError:
            self.volume_view.setBatteryLevel_(None)

    def parse_battery_level(self, output, current_output):
        lines = output.splitlines()
        device_found = False
        left_battery = None
        right_battery = None
        for i, line in enumerate(lines):
            if current_output in line:
                device_found = True
            if device_found:
                if "Left Battery Level" in line:
                    try:
                        left_battery = int(line.split(":")[1].strip().strip("%"))
                    except (IndexError, ValueError):
                        pass
                elif "Right Battery Level" in line:
                    try:
                        right_battery = int(line.split(":")[1].strip().strip("%"))
                    except (IndexError, ValueError):
                        pass
                if left_battery is not None and right_battery is not None:
                    break
        if left_battery is not None and right_battery is not None:
            return (left_battery + right_battery) // 2
        elif left_battery is not None:
            return left_battery
        elif right_battery is not None:
            return right_battery
        return None

if __name__ == "__main__":
    MenuVolumeBarApp()