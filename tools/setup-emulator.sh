#!/usr/bin/env bash
# Download Ubuntu/Mint packages and unpack locally. No sudo or system install.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TOOL_ROOT=${DK64_TOOL_ROOT:-"$ROOT/tools"}
mkdir -p "$TOOL_ROOT/packages" "$TOOL_ROOT/emulator"
cd "$TOOL_ROOT/packages"
apt-get -o Acquire::Retries=0 download \
  mupen64plus-ui-console libmupen64plus2 mupen64plus-data \
  mupen64plus-video-glide64mk2 mupen64plus-video-rice \
  mupen64plus-input-sdl mupen64plus-audio-sdl mupen64plus-rsp-hle \
  libsdl2-net-2.0-0 xdotool libxdo3 xvfb xserver-common
for package in ./*.deb; do
  dpkg-deb -x "$package" "$TOOL_ROOT/emulator"
done
sha256sum ./*.deb > SHA256SUMS
echo 'Ready. Launch with tools/play.sh or tools/control.py.'
