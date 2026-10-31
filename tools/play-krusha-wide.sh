#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export DK64_RESOLUTION=${DK64_RESOLUTION:-1280x720}
export DK64_STRETCH=1
exec "$ROOT/tools/play-krusha.sh" "$@"
