#!/usr/bin/env bash
# Optional, pinned Linux x86-64 compatibility-test frontend. No system install.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
BASE=${DK64_LIBRETRO_ROOT:-"$ROOT/runtime/libretro-tools"}
mkdir -p "$BASE/packages" "$BASE/retroarch" "$BASE/core" "$BASE/info"
BASE=$(cd -- "$BASE" && pwd)
fetch() {
  local name=$1 expected=$2 url=$3
  if [[ ! -f "$BASE/packages/$name" ]]; then
    curl --fail --location --retry 2 "$url" -o "$BASE/packages/$name.part"
    mv -- "$BASE/packages/$name.part" "$BASE/packages/$name"
  fi
  printf '%s  %s\n' "$expected" "$BASE/packages/$name" | sha256sum --check
}
fetch 'retroarch_1.18.0+dfsg-1_amd64.deb' \
  992676fcd5e2fb533498a9ea6976a3a40cbea7bc7d4a03dbe7c503e2e49f9b91 \
  'https://archive.ubuntu.com/ubuntu/pool/universe/r/retroarch/retroarch_1.18.0+dfsg-1_amd64.deb'
# The buildbot URL moves. Reject a different build: RDRAM diagnostics are pinned
# to this ELF. A later core needs a deliberate lookup/validation update.
fetch 'mupen64plus_next_libretro.so.zip' \
  836b20112870b9764103d986819e8559571122c8550c74e5da9238a4ffd67700 \
  'https://buildbot.libretro.com/nightly/linux/x86_64/latest/mupen64plus_next_libretro.so.zip'
dpkg-deb -x "$BASE/packages/retroarch_1.18.0+dfsg-1_amd64.deb" "$BASE/retroarch"
unzip -o "$BASE/packages/mupen64plus_next_libretro.so.zip" -d "$BASE/core"
printf '%s  %s\n' \
  26f2b4ec722558d77bc9e1582e62ab80c84190bb20dfadc48a148e6210c8775e \
  "$BASE/core/mupen64plus_next_libretro.so" | sha256sum --check
curl --fail --location \
 'https://raw.githubusercontent.com/libretro/libretro-core-info/master/mupen64plus_next_libretro.info' \
 -o "$BASE/info/mupen64plus_next_libretro.info"
cp -- "$BASE/info/mupen64plus_next_libretro.info" "$BASE/info/mupen64plus_next_test_libretro.info"
gcc -shared -fPIC -O2 "$ROOT/tools/libretro-test-input.c" \
 -Wl,--no-as-needed "$BASE/core/mupen64plus_next_libretro.so" -ldl \
 -o "$BASE/core/mupen64plus_next_test_libretro.so"
printf 'Ready: set DK64_LIBRETRO_ROOT=%s\n' "$BASE"
