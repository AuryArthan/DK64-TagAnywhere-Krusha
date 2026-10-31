#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
VADPCM_SOURCE="$ROOT/tools/vadpcm"
VADPCM_COMMIT=413d52043a928c5fac066ccda1e69b73c7f7132b
if [[ ! -d "$VADPCM_SOURCE/.git" ]]; then
  git clone https://github.com/depp/vadpcm.git "$VADPCM_SOURCE"
  git -C "$VADPCM_SOURCE" checkout --detach "$VADPCM_COMMIT"
fi
if [[ $(git -C "$VADPCM_SOURCE" rev-parse HEAD) != "$VADPCM_COMMIT" ]]; then
  echo "Expected VADPCM source revision $VADPCM_COMMIT; existing checkout was left intact." >&2
  exit 1
fi
mkdir -p "$VADPCM_SOURCE/build"
cc -std=c17 -O2 -I"$VADPCM_SOURCE" "$VADPCM_SOURCE"/codec/*.c \
  "$VADPCM_SOURCE"/common/*.c "$VADPCM_SOURCE"/vadpcm/*.c \
  -lm -pthread -o "$VADPCM_SOURCE/build/vadpcm"
"$VADPCM_SOURCE/build/vadpcm" encode --help
