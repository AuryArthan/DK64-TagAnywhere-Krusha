#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export DK64_ROM="$ROOT/rom/dk64-krusha-dev.z64"
exec /usr/bin/python3 "$ROOT/tools/control.py" "$@"
