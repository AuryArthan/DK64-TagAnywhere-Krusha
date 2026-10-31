#!/usr/bin/env python3
"""Read-only orientation. No build, emulator, edits, state loads or network calls."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SNAPSHOT = json.loads((HERE / 'snapshot.json').read_text())
WORKSPACE = REPO.parent if (REPO.parent / 'tools/build-krusha.sh').is_file() else None


def git(*args):
    p = subprocess.run(['git', '-C', str(REPO), *args], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.strip() if p.returncode == 0 else {'unavailable': p.stderr.strip()}


def identity(path, expected):
    if not path.is_file():
        return {'path': str(path), 'present': False}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {'path': str(path), 'present': True, 'size': path.stat().st_size,
            'sha256': digest, 'matches_dated_snapshot': digest == expected}


TOOL_ROOT = Path(os.environ.get('DK64_TOOL_ROOT', REPO / 'tools')).resolve()
result = {
    'read_only': True,
    'snapshot_date': SNAPSHOT['snapshot_date'],
    'accepted_version': SNAPSHOT['latest_accepted_version'],
    'accepted_checkpoint_rom_sha256': SNAPSHOT['rom_sha256'],
    'unreleased_development': SNAPSHOT.get('unreleased_development'),
    'repository': str(REPO),
    'workspace': str(WORKSPACE) if WORKSPACE else None,
    'git': {'head': git('rev-parse', 'HEAD'),
            'branch': git('branch', '--show-current'),
            'status': git('status', '--short'),
            'v042_gameplay_commit': git('rev-parse', 'v0.4.2^{}')},
    'development_rom': identity(REPO / 'rom/dk64-krusha-dev.z64', SNAPSHOT.get('unreleased_development', {}).get('rom_sha256', SNAPSHOT['rom_sha256'])),
    'binary_cache': str(TOOL_ROOT),
    'cached_tools_present': {n: (TOOL_ROOT / n).is_file() for n in [
        'n64chain/tools/bin/mips64-elf-gcc', 'build-tools/armips/armips',
        'build-tools/bin/gzip-1.2.4', 'emulator/usr/games/mupen64plus']},
    'maintained_workflow_present': (REPO / 'tools/build-krusha.sh').is_file(),
    'repo_runtime': str(REPO / 'runtime'),
    'python_has_pillow': importlib.util.find_spec('PIL') is not None,
    'note': 'This is a dated reference, not a restore command. Investigate differences; preserve newer work.'
}
if WORKSPACE:
    profile = REPO / 'runtime/krusha/current'
    result['original_rom'] = identity(REPO / 'rom/dk64.z64',
                                      SNAPSHOT['original_rom_sha256'])
    result['normal_profile'] = {'path': str(profile), 'target': str(profile.resolve()),
                                'present': profile.exists()}
    result['checkpoint_present'] = (WORKSPACE / 'runtime/checkpoints/v0.4.2/checkpoint.json').is_file()
    result['latest_qa_present'] = (WORKSPACE / 'runtime/krusha/tree-tag-fix-review/summary.json').is_file()
else:
    result['note'] += ' Parent historical workspace is absent; maintained tools/ work from this clone. Supply dependencies, ROM and test fixture as documented.'
print(json.dumps(result, indent=2))
