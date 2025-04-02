// coreaudio.c
#include <CoreAudio/CoreAudio.h>
#include <AudioToolbox/AudioToolbox.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <string.h>

// Callback function pointer type để thông báo thay đổi thiết bị
typedef void (*DeviceChangeCallback)(const char* newDeviceName);

// Biến toàn cục để lưu callback từ Python
static DeviceChangeCallback deviceChangeCallback = NULL;

// Hàm lấy tên thiết bị
void getDeviceName(AudioDeviceID deviceID, char* name, UInt32 nameSize) {
    AudioObjectPropertyAddress propertyAddress = {
        kAudioObjectPropertyName,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    CFStringRef deviceName = NULL;
    UInt32 size = sizeof(deviceName);
    OSStatus status = AudioObjectGetPropertyData(deviceID, &propertyAddress, 0, NULL, &size, &deviceName);
    if (status == noErr && deviceName != NULL) {
        CFStringGetCString(deviceName, name, nameSize, kCFStringEncodingUTF8);
        CFRelease(deviceName);
    } else {
        snprintf(name, nameSize, "Unknown Device");
    }
}

// Hàm lấy danh sách tất cả thiết bị đầu ra và tìm thiết bị đang hoạt động
AudioDeviceID getActiveOutputDevice() {
    // Ưu tiên lấy thiết bị đầu ra mặc định
    AudioDeviceID activeDeviceID = 0;
    AudioObjectPropertyAddress defaultDeviceAddress = {
        kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    UInt32 size = sizeof(activeDeviceID);
    OSStatus status = AudioObjectGetPropertyData(kAudioObjectSystemObject, &defaultDeviceAddress, 0, NULL, &size, &activeDeviceID);
    if (status == noErr && activeDeviceID != 0) {
        return activeDeviceID;
    }

    // Dự phòng: liệt kê tất cả thiết bị và tìm thiết bị đang hoạt động
    AudioObjectPropertyAddress propertyAddress = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    UInt32 dataSize = 0;
    status = AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &propertyAddress, 0, NULL, &dataSize);
    if (status != noErr) {
        return 0;
    }

    UInt32 deviceCount = dataSize / sizeof(AudioDeviceID);
    AudioDeviceID *deviceIDs = (AudioDeviceID *)malloc(dataSize);
    status = AudioObjectGetPropertyData(kAudioObjectSystemObject, &propertyAddress, 0, NULL, &dataSize, deviceIDs);
    if (status != noErr) {
        free(deviceIDs);
        return 0;
    }

    activeDeviceID = 0;
    AudioObjectPropertyAddress runningAddress = {
        kAudioDevicePropertyDeviceIsRunningSomewhere,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    for (UInt32 i = 0; i < deviceCount; i++) {
        UInt32 isRunning = 0;
        UInt32 runningSize = sizeof(isRunning);
        status = AudioObjectGetPropertyData(deviceIDs[i], &runningAddress, 0, NULL, &runningSize, &isRunning);
        if (status == noErr && isRunning) {
            AudioObjectPropertyAddress scopeAddress = {
                kAudioDevicePropertyScopeOutput,
                kAudioObjectPropertyScopeGlobal,
                kAudioObjectPropertyElementMain
            };
            if (AudioObjectHasProperty(deviceIDs[i], &scopeAddress)) {
                activeDeviceID = deviceIDs[i];
                break;
            }
        }
    }

    free(deviceIDs);
    return activeDeviceID;
}

// Hàm callback khi thiết bị đầu ra thay đổi
static OSStatus audioDeviceListener(
    AudioObjectID inObjectID,
    UInt32 inNumberAddresses,
    const AudioObjectPropertyAddress inAddresses[],
    void* inClientData) {
    if (deviceChangeCallback != NULL) {
        AudioDeviceID newDeviceID = getActiveOutputDevice();
        if (newDeviceID != 0) {
            char deviceName[256];
            getDeviceName(newDeviceID, deviceName, sizeof(deviceName));
            deviceChangeCallback(deviceName);
        }
    }
    return noErr;
}

// Hàm đăng ký listener cho thay đổi thiết bị
void registerDeviceListener(DeviceChangeCallback callback) {
    deviceChangeCallback = callback;

    AudioObjectPropertyAddress propertyAddress = {
        kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    OSStatus status = AudioObjectAddPropertyListener(
        kAudioObjectSystemObject,
        &propertyAddress,
        audioDeviceListener,
        NULL
    );

    if (status != noErr) {
        printf("Failed to register device listener: %d\n", status);
    }
}

// Hàm lấy tên thiết bị đầu ra hiện tại
const char* getCurrentOutputDevice() {
    AudioDeviceID deviceID = getActiveOutputDevice();
    if (deviceID == 0) {
        return "Unknown Device";
    }

    static char deviceName[256];
    getDeviceName(deviceID, deviceName, sizeof(deviceName));
    return deviceName;
}

// Hàm lấy âm lượng hệ thống (trả về giá trị từ 0-100)
float getSystemVolume() {
    AudioDeviceID deviceID = getActiveOutputDevice();
    if (deviceID == 0) {
        return -1.0;
    }

    AudioObjectPropertyAddress propertyAddress = {
        kAudioDevicePropertyVolumeScalar,
        kAudioObjectPropertyScopeOutput,
        kAudioObjectPropertyElementMain
    };

    if (!AudioObjectHasProperty(deviceID, &propertyAddress)) {
        return -1.0;
    }

    Float32 volume;
    UInt32 size = sizeof(volume);
    OSStatus status = AudioObjectGetPropertyData(deviceID, &propertyAddress, 0, NULL, &size, &volume);
    if (status != noErr) {
        return -1.0;
    }

    return volume * 100.0;
}

// Hàm đặt âm lượng hệ thống (giá trị từ 0-100)
void setSystemVolume(float volume) {
    AudioDeviceID deviceID = getActiveOutputDevice();
    if (deviceID == 0) {
        return;
    }

    AudioObjectPropertyAddress propertyAddress = {
        kAudioDevicePropertyVolumeScalar,
        kAudioObjectPropertyScopeOutput,
        kAudioObjectPropertyElementMain
    };

    if (!AudioObjectHasProperty(deviceID, &propertyAddress)) {
        return;
    }

    Boolean isWritable;
    OSStatus status = AudioObjectIsPropertySettable(deviceID, &propertyAddress, &isWritable);
    if (status != noErr || !isWritable) {
        return;
    }

    Float32 volumeScalar = volume / 100.0;
    UInt32 size = sizeof(volumeScalar);
    status = AudioObjectSetPropertyData(deviceID, &propertyAddress, 0, NULL, size, &volumeScalar);
}

// Hàm kiểm tra trạng thái mute
int getSystemMuted() {
    AudioDeviceID deviceID = getActiveOutputDevice();
    if (deviceID == 0) {
        return -1;
    }

    AudioObjectPropertyAddress propertyAddress = {
        kAudioDevicePropertyMute,
        kAudioObjectPropertyScopeOutput,
        kAudioObjectPropertyElementMain
    };

    if (!AudioObjectHasProperty(deviceID, &propertyAddress)) {
        return -1;
    }

    UInt32 muted;
    UInt32 size = sizeof(muted);
    OSStatus status = AudioObjectGetPropertyData(deviceID, &propertyAddress, 0, NULL, &size, &muted);
    if (status != noErr) {
        return -1;
    }

    return muted;
}