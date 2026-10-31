#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TOOL_ROOT=${DK64_TOOL_ROOT:-"$ROOT/tools"}
export PATH="$TOOL_ROOT/n64chain/tools/bin:$PATH"
export LD_LIBRARY_PATH="$TOOL_ROOT/n64chain/tools/x86_64-pc-linux-gnu/mips64-elf/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export ARMIPS=${ARMIPS:-"$TOOL_ROOT/build-tools/armips/armips"}
export N64_GZIP=${N64_GZIP:-"$TOOL_ROOT/build-tools/bin/gzip-1.2.4"}
mkdir -p "$ROOT/rom"
if [[ ! -f "$ROOT/rom/dk64.z64" ]]; then
  echo "Place the original USA ROM at $ROOT/rom/dk64.z64" >&2
  exit 1
fi
cd "$ROOT"
/usr/bin/python3 build/build.py
/usr/bin/python3 - "$ROOT" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
repo = root
rom = repo / 'rom/dk64-krusha-dev.z64'
data = rom.read_bytes()
digest = hashlib.sha256(data).hexdigest()
record = root / 'runtime/krusha'
record.mkdir(parents=True, exist_ok=True)
profile = root / 'runtime/roms' / digest
profile.mkdir(parents=True, exist_ok=True)
link = record / 'current'
if link.is_symlink():
    link.unlink()
elif link.exists():
    raise SystemExit('runtime/krusha/current must be a symlink, not a directory')
link.symlink_to('../roms/' + digest, target_is_directory=True)
upstream = 'e9ca72f5070c7e4bad69d37382c5a0798b06462f'
tracked = subprocess.check_output(['git', '-C', str(repo), 'diff', '--name-only', upstream], text=True).splitlines()
added = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()
source_changes = sorted(set(tracked + added))
patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', upstream])
for name in added:
    result = subprocess.run(['git', 'diff', '--no-index', '--binary', '--', '/dev/null', name],
                            cwd=repo, stdout=subprocess.PIPE, check=False)
    if result.returncode not in (0, 1):
        raise SystemExit('Could not preserve source diff for ' + name)
    patch += result.stdout
(record / 'source-changes.patch').write_bytes(patch)
manifest = {'rom': str(rom.relative_to(root)),
    'source_commit': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(),
    'upstream_commit': upstream,
    'size': len(data), 'sha1': hashlib.sha1(data).hexdigest(),
    'sha256': digest, 'md5': hashlib.md5(data).hexdigest(),
    'compiler': 'n64chain GCC 9.1.0', 'assembler': 'armips 0.11.0', 'gzip': '1.2.4',
    'baseline_sha256': '9fc6f92cbd27632af572dfb9961164148f4054a7dffcf51cb17d02ac4d60fa47',
    'integration': 'Sixth adventure character; no global identity spoof',
    'source_changes': source_changes}
(record / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY

/usr/bin/python3 "$ROOT/tools/make-bps.py" "$ROOT/rom/dk64.z64" "$ROOT/rom/dk64-krusha-dev.z64" "$ROOT/runtime/krusha/dk64-krusha-adventure.bps"
