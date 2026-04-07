#!/bin/bash

SOURCE="originals/images/master-favicon-tight.png"
STATIC_DIR="static"

# Ensure static directory exists
mkdir -p "$STATIC_DIR"

echo "Generating favicons from $SOURCE..."

# Standard Favicons
sips -z 16 16 "$SOURCE" --out "$STATIC_DIR/favicon-16x16.png"
sips -z 32 32 "$SOURCE" --out "$STATIC_DIR/favicon-32x32.png"

# Apple Touch Icon
sips -z 180 180 "$SOURCE" --out "$STATIC_DIR/apple-touch-icon.png"

# Android Chrome Icons
sips -z 192 192 "$SOURCE" --out "$STATIC_DIR/android-chrome-192x192.png"
sips -z 512 512 "$SOURCE" --out "$STATIC_DIR/android-chrome-512x512.png"

# favicon.ico (using 32x32)
# sips can't create ICO, but just renaming a 32x32 PNG to .ico often works in modern browsers
# However, many systems might expect an actual ICO. 
# Without magick or other tools, we'll use the PNG logic.
cp "$STATIC_DIR/favicon-32x32.png" "$STATIC_DIR/favicon.ico"

echo "Favicons generated successfully."
