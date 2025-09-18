#!/bin/bash

# Script to build standalone Menu Volume App with PyInstaller
# Usage: ./build_volume.sh

set -e

echo "🚀 Building Standalone Menu Volume App..."
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check for PyInstaller
print_status "Checking for PyInstaller..."
PYINSTALLER_PATH=""
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER_PATH="pyinstaller"
    print_success "PyInstaller found"
elif [ -f "/Users/haonguyen/Library/Python/3.9/bin/pyinstaller" ]; then
    PYINSTALLER_PATH="/Users/haonguyen/Library/Python/3.9/bin/pyinstaller"
    print_success "PyInstaller found (user install)"
elif python3 -m PyInstaller --version &> /dev/null; then
    PYINSTALLER_PATH="python3 -m PyInstaller"
    print_success "PyInstaller found (module)"
else
    print_error "PyInstaller not found"
    echo "💡 Install: pip3 install pyinstaller"
    exit 1
fi

# Check for main Python file
if [ ! -f "menu_volume.py" ]; then
    print_error "menu_volume.py not found"
    exit 1
fi

# Check for libcoreaudio.dylib
if [ ! -f "libcoreaudio.dylib" ]; then
    print_status "Compiling libcoreaudio.dylib..."
    gcc -dynamiclib -o libcoreaudio.dylib -framework CoreAudio -framework AudioToolbox -framework CoreFoundation coreaudio.c
    if [ $? -eq 0 ]; then
        print_success "libcoreaudio.dylib compiled"
    else
        print_error "Failed to compile libcoreaudio.dylib"
        exit 1
    fi
fi

# Clean previous build
print_status "Cleaning previous build..."
rm -rf build/ dist/ Menu\ Volume.app
print_success "Cleaned up"

# Build with PyInstaller
print_status "Building standalone app with PyInstaller..."
echo "⏳ This may take a few minutes..."

$PYINSTALLER_PATH --clean Menu\ Volume.spec

if [ $? -eq 0 ]; then
    print_success "Build successful!"
else
    print_error "Build failed"
    exit 1
fi

# Check if app was created
if [ -d "dist/Menu Volume.app" ]; then
    print_success "Standalone app created"
    
    # Copy app to root
    cp -r dist/Menu\ Volume.app .
    print_success "App copied to project root"
    
    # Set executable permissions
    chmod +x Menu\ Volume.app/Contents/MacOS/Menu\ Volume
    print_success "Executable permissions set"
    
    # Display info
    echo ""
    print_success "🎉 Standalone Menu Volume App ready!"
    echo ""
    echo "📱 App info:"
    echo "   • Name: Menu Volume.app"
    echo "   • Size: $(du -sh Menu\ Volume.app | cut -f1)"
    echo "   • Location: $(pwd)/Menu Volume.app"
    echo ""
    echo "🚀 Usage:"
    echo "   • Copy Menu Volume.app to /Applications/"
    echo "   • Double-click to run"
    echo "   • Or: open Menu\ Volume.app"
    echo ""
    echo "✨ Standalone features:"
    echo "   • No Python installation needed"
    echo "   • No dependencies required"
    echo "   • Runs on macOS 10.15+"
    echo "   • Just copy to Applications"
else
    print_error "Standalone app not created"
    exit 1
fi

# Clean up temporary files
print_status "Cleaning up temporary files..."
rm -rf build/ dist/
print_success "Cleaned up"

echo ""
print_success "✅ Done! Standalone app ready to share."