```bash
   #!/bin/bash

   # Biến môi trường và đường dẫn
   PYINSTALLER_PATH="$(which pyinstaller)"  # Tự động lấy đường dẫn của PyInstaller
   SOURCE_DIR="."
   OUTPUT_DIR="$SOURCE_DIR/dist"
   LIB_PATH="$SOURCE_DIR/libcoreaudio.dylib"
   ICON_PATH="$SOURCE_DIR/level_icon.png"

   # Kiểm tra PyInstaller
   if [ -z "$PYINSTALLER_PATH" ]; then
       echo "PyInstaller không tìm thấy. Vui lòng cài đặt bằng: pip install pyinstaller"
       exit 1
   fi

   # Xóa build cũ nếu tồn tại
   rm -rf build dist

   # Build ứng dụng với PyInstaller
   "$PYINSTALLER_PATH" --clean \
     --add-data "$LIB_PATH:." \
     --add-data "$ICON_PATH:." \
     --hidden-import AppKit \
     --hidden-import objc \
     --hidden-import ctypes \
     --windowed \
     --name "Menu Volume" \
     "menu_volume.py"

   # Di chuyển kết quả vào thư mục mong muốn
   mv "dist/Menu Volume.app" "$OUTPUT_DIR"

   echo "Build hoàn tất. Ứng dụng nằm trong $OUTPUT_DIR/Menu Volume.app"
   ```