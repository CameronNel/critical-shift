#!/usr/bin/env bash
set -euo pipefail
V=5.2.1
D=/tmp/gullet-quality-toolchain
mkdir -p "$D"
cd "$D"
curl -fsSL --retry 2 --connect-timeout 25 --max-time 300 "https://download.blender.org/release/Blender5.2/blender-${V}-linux-x64.tar.xz" -o blender.tar.xz
curl -fsSL --retry 2 --max-time 60 "https://download.blender.org/release/Blender5.2/blender-${V}.sha256" -o checksums.txt
EXPECTED=$(grep "blender-${V}-linux-x64.tar.xz" checksums.txt | awk '{print $1}')
test -n "$EXPECTED"
printf '%s  blender.tar.xz\n' "$EXPECTED" | sha256sum --check -
tar -xf blender.tar.xz
sudo apt-get update -qq
sudo apt-get install -y -qq libxrender1 libxi6 libxfixes3 libxkbcommon0 libsm6 libgl1 >/dev/null
echo "$D/blender-${V}-linux-x64" >> "$GITHUB_PATH"
"$D/blender-${V}-linux-x64/blender" -b --factory-startup --python-expr "import bpy; print('VERIFIED_BLENDER',bpy.app.version_string)"
