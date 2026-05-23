#!/bin/bash
# Rebuild typing_game.h5p from the current typing_game.html.
#
# Wraps the standalone HTML in an H5P Iframe Embedder package so it can be
# uploaded to Moodle's Content Bank and embedded as an H5P activity.
#
# Requirements:
#   - typing_game.html present in this directory
#   - /tmp/iframe_embedder.h5p (the H5P.IFrameEmbed library bundle,
#     one-time download from https://api.h5p.org/v1/content-types/H5P.IFrameEmbed)
#
# Output: typing_game.h5p in this directory.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REF="/tmp/iframe_embedder.h5p"

if [ ! -f "$REF" ]; then
  echo "Downloading H5P.IFrameEmbed library bundle..."
  curl -sSL -o "$REF" "https://api.h5p.org/v1/content-types/H5P.IFrameEmbed"
fi

if [ ! -f "$HERE/typing_game.html" ]; then
  echo "ERROR: $HERE/typing_game.html not found" >&2
  exit 1
fi

# Build in a scratch directory
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT

# Copy the game file into content/
mkdir -p "$BUILD/content"
cp "$HERE/typing_game.html" "$BUILD/content/typing_game.html"

# Copy library files from the reference H5P (skip its content/ and h5p.json)
cd "$BUILD"
unzip -q -o "$REF" -x 'content/*' 'h5p.json'

# Write our own manifest
cat > h5p.json <<'JSON'
{
  "title": "ERISE_DSM Typing Game",
  "language": "en",
  "mainLibrary": "H5P.IFrameEmbed",
  "embedTypes": ["div"],
  "license": "U",
  "defaultLanguage": "en",
  "preloadedDependencies": [
    {"machineName": "H5P.IFrameEmbed", "majorVersion": "1", "minorVersion": "0"}
  ]
}
JSON

# Write content.json pointing at our HTML file. The H5P.IFrameEmbed library
# resolves the `source` path against content/, so "typing_game.html" works.
cat > content/content.json <<'JSON'
{
  "width": "100%",
  "minWidth": "300px",
  "height": "900px",
  "source": "typing_game.html",
  "resizeSupported": true
}
JSON

# Zip it back up as the output .h5p
rm -f "$HERE/typing_game.h5p"
zip -qr "$HERE/typing_game.h5p" .

cd "$HERE"
ls -la typing_game.h5p
echo "Built typing_game.h5p — upload to Moodle Content Bank to test."
