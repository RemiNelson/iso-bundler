#!/bin/bash
# Builds "ISO Bundler.app", a thin wrapper that launches this project's
# existing venv (`python -m isobundler`) so it can be double-clicked from
# Finder instead of run from a terminal.
#
# Usage: packaging/make_app.sh [install_dir]   (default: ~/Applications)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="ISO Bundler"
INSTALL_DIR="${1:-$HOME/Applications}"
APP_PATH="$INSTALL_DIR/$APP_NAME.app"

if [ ! -x "$REPO_DIR/.venv/bin/python" ]; then
    echo "error: $REPO_DIR/.venv doesn't exist yet." >&2
    echo "Set it up first: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

mkdir -p "$INSTALL_DIR"
rm -rf "$APP_PATH"
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

ICON_SRC="$REPO_DIR/packaging/icon.icns"
if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$APP_PATH/Contents/Resources/icon.icns"
fi

cat > "$APP_PATH/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.reminelson.isobundler</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$APP_PATH/Contents/MacOS/launch" <<LAUNCH
#!/bin/bash
cd "$REPO_DIR"
exec "$REPO_DIR/.venv/bin/python" -m isobundler >> "\$HOME/Library/Logs/isobundler.log" 2>&1
LAUNCH
chmod +x "$APP_PATH/Contents/MacOS/launch"

echo "Built: $APP_PATH"
echo "Logs (if it fails to launch): ~/Library/Logs/isobundler.log"
