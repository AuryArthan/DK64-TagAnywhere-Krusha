#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TOOL_ROOT=${DK64_TOOL_ROOT:-"$ROOT/tools"}
export LD_LIBRARY_PATH="$TOOL_ROOT/emulator/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
ROM=${DK64_ROM:-"$ROOT/rom/dk64-krusha-dev.z64"}
ROM_HASH=$(sha256sum -- "$ROM")
ROM_HASH=${ROM_HASH%% *}
RUN="$ROOT/runtime"
if [[ "$ROM_HASH" != b6347d9f1f75d38a88d829b4f80b1acf0d93344170a5fbe9546c484dae416ce3 ]]; then
  RUN="$ROOT/runtime/roms/$ROM_HASH"
fi
RUN=${DK64_RUNTIME:-$RUN}
export XDG_CONFIG_HOME="$RUN/xdg-config"
export XDG_DATA_HOME="$RUN/xdg-data"
export XDG_CACHE_HOME="$RUN/xdg-cache"
mkdir -p "$RUN/"{config,saves,states,screenshots,logs,xdg-config,xdg-data,xdg-cache}
if [[ ! -f "$RUN/config/mupen64plus.cfg" ]]; then
  cp -- "$ROOT/tools/config/mupen64plus.cfg" "$RUN/config/mupen64plus.cfg"
fi
DATA="$TOOL_ROOT/emulator/usr/share/games/mupen64plus"
DISPLAY_OPTIONS=()
if [[ ${DK64_STRETCH:-0} == 1 ]]; then
  DISPLAY_OPTIONS+=(--set 'Video-Glide64mk2[aspect]=2' --set 'Video-Glide64mk2[adjust_aspect]=0')
fi
if [[ "$ROM_HASH" != b6347d9f1f75d38a88d829b4f80b1acf0d93344170a5fbe9546c484dae416ce3 ]]; then
  DATA="$RUN/data"
  /usr/bin/python3 "$ROOT/tools/configure-dk64-rom.py" "$ROM" "$DATA"
fi
exec "$TOOL_ROOT/emulator/usr/games/mupen64plus" \
  --corelib "$TOOL_ROOT/emulator/usr/lib/x86_64-linux-gnu/libmupen64plus.so.2" \
  --plugindir "$TOOL_ROOT/emulator/usr/lib/x86_64-linux-gnu/mupen64plus" \
  --datadir "$DATA" \
  --configdir "$RUN/config" --sshotdir "$RUN/screenshots" \
  --set "Core[SaveStatePath]=$RUN/states" \
  --set "Core[SaveSRAMPath]=$RUN/saves" \
  --set 'Core[DisableExtraMem]=False' \
  --set 'Core[CountPerOp]=1' \
  --gfx "${DK64_GFX:-mupen64plus-video-glide64mk2.so}" \
  --audio "${DK64_AUDIO:-mupen64plus-audio-sdl.so}" \
  --resolution "${DK64_RESOLUTION:-640x480}" --windowed --noosd "${DISPLAY_OPTIONS[@]}" "$@" "$ROM"
