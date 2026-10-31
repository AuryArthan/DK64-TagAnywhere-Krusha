#!/usr/bin/env bash
# Project-local Linux build prerequisites. No sudo or system package install.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TOOL_ROOT=${DK64_TOOL_ROOT:-"$ROOT/tools"}
mkdir -p "$TOOL_ROOT/"{downloads,packages,n64chain,armips-src,build-tools/bin}
if [[ ! -f "$TOOL_ROOT/downloads/n64chain-linux-9.1.0.tgz" ]]; then
  curl -fL https://github.com/tj90241/n64chain/releases/download/9.1.0/n64chain-linux.tgz \
    -o "$TOOL_ROOT/downloads/n64chain-linux-9.1.0.tgz"
fi
echo "6d0ab3ab768bf8eaba8196e9d16a92f6329165b61361ae8f44accd333fe8d8cd  $TOOL_ROOT/downloads/n64chain-linux-9.1.0.tgz" | sha256sum -c -
if [[ ! -x "$TOOL_ROOT/n64chain/tools/bin/mips64-elf-gcc" ]]; then
  tar -xzf "$TOOL_ROOT/downloads/n64chain-linux-9.1.0.tgz" -C "$TOOL_ROOT/n64chain"
fi
if [[ ! -x "$TOOL_ROOT/build-tools/usr/bin/cmake" ]]; then
  cd "$TOOL_ROOT/packages"
  apt-get -o Acquire::Retries=0 download cmake cmake-data librhash0 libjsoncpp25
  for package in cmake_*.deb cmake-data_*.deb librhash0_*.deb libjsoncpp25_*.deb; do
    dpkg-deb -x "$package" "$TOOL_ROOT/build-tools"
  done
fi
if [[ ! -f "$TOOL_ROOT/downloads/armips-v0.11.0.tar.gz" ]]; then
  curl -fL https://github.com/Kingcom/armips/archive/refs/tags/v0.11.0.tar.gz \
    -o "$TOOL_ROOT/downloads/armips-v0.11.0.tar.gz"
fi
echo "c94e29dfda3bdf853590d825562b9c73a3d8e8e995555e021c6b2a6451572681  $TOOL_ROOT/downloads/armips-v0.11.0.tar.gz" | sha256sum -c -
if [[ ! -f "$TOOL_ROOT/armips-src/CMakeLists.txt" ]]; then
  tar -xzf "$TOOL_ROOT/downloads/armips-v0.11.0.tar.gz" -C "$TOOL_ROOT/armips-src" --strip-components=1
fi
# Old armips relied on transitive includes that GCC 13 no longer supplies.
/usr/bin/python3 - "$TOOL_ROOT/armips-src/Core/ExpressionFunctions.cpp" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1]); text = p.read_text()
if '#include <limits>' not in text:
    p.write_text(text.replace('#include "stdafx.h"', '#include "stdafx.h"\n#include <limits>\n#include <cstdint>'))
PY
export LD_LIBRARY_PATH="$TOOL_ROOT/build-tools/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
CMAKE="$TOOL_ROOT/build-tools/usr/bin/cmake"
"$CMAKE" -S "$TOOL_ROOT/armips-src" -B "$TOOL_ROOT/build-tools/armips" -DCMAKE_BUILD_TYPE=Release
"$CMAKE" --build "$TOOL_ROOT/build-tools/armips" --target armips-bin -j 2
if [[ ! -x "$TOOL_ROOT/build-tools/bin/gzip-1.2.4" ]]; then
  archive="$TOOL_ROOT/downloads/gzip-1.2.4.tar.gz"
  if [[ ! -f "$archive" ]]; then
    curl -fL https://ftp.gnu.org/gnu/gzip/gzip-1.2.4.tar.gz -o "$archive"
  fi
  echo "1ca41818a23c9c59ef1d5e1d00c0d5eaa2285d931c0fb059637d7c0cc02ad967  $archive" | sha256sum -c -
  mkdir -p "$TOOL_ROOT/build-tools/gzip-src"
  tar -xzf "$archive" -C "$TOOL_ROOT/build-tools/gzip-src" --strip-components=1
  cd "$TOOL_ROOT/build-tools/gzip-src"
  ./configure
  make -j2 CFLAGS="-O2 -fcommon"
  cp gzip "$TOOL_ROOT/build-tools/bin/gzip-1.2.4"
  cp COPYING "$TOOL_ROOT/build-tools/bin/gzip-COPYING"
fi
echo 'Build tools ready; run ./tools/build-krusha.sh'
