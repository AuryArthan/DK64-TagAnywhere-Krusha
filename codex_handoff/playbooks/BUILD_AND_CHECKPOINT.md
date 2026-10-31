# Playbook: build, verify and preserve a requested version

**Workflow migration, 2026-10-31:** maintained scripts now live inside the repo.
Start with [tools/README.md](../../tools/README.md) for current runnable commands
and required fixtures/output variables. Parent-workspace commands and hardcoded
historical-runner cautions below describe the legacy setup.

Use this when implementing an authorized game change, restoring a build, or
when the user explicitly asks to save a new checkpoint. Merely reading this
handoff does not request a build, version increment or publication.

## Before editing

From the workspace root:

```sh
git -C dk64-tag-anywhere status --short
git -C dk64-tag-anywhere log -3 --oneline
git -C dk64-tag-anywhere tag --list
sha256sum dk64-tag-anywhere/rom/dk64-krusha-dev.z64
```

Inspect existing changes and preserve user work. The accepted game may sit at
an older commit than HEAD because later commits only add docs/knowledge. Do not
rewrite tagged releases to make their README match a newer documentation commit.

## Build

```sh
./tools/build-krusha.sh
```

This configures the local n64chain GCC 9.1.0, armips 0.11.0 and gzip 1.2.4,
compiles/repackages the ROM, writes a manifest and source diff, verifies the BPS
patch against the original USA ROM, and updates `runtime/krusha/current` to the
new hash profile. It does **not** automatically migrate the user's EEPROM or
make old save states compatible. Back up the old profile before migration.

For a standalone clone, use [docs/BUILDING.md](../../docs/BUILDING.md) instead.
The source SHA-1 check protects the private original. Build output is
`dk64-tag-anywhere/rom/dk64-krusha-dev.z64`; `DK64_BUILD_ROM` can change it in the
underlying Python builder. A broken build can remove/replace the dev output;
frozen checkpoint ROMs are the recovery route, not an unbacked modified file.

Compressed static/menu/shop overlays have fixed capacities. Preserve the build's
capacity checks, native allocation/reference tracking and final header checksum.
Do not fix an overflow by overwriting neighboring ROM data. New MIPS hooks need
verified displaced instructions, calling convention and cache handling.

## Validation

Choose checks appropriate to the code change using the testing playbook. Archive
results under a new review/run directory, including exact ROM hash and fixture
policy. Read JSON completion/checks, not only the console banner. A build passing
is not gameplay passing. A docs-only edit needs link/image/content checks, not a
new full gameplay certification.

For a known candidate, validate:

- Big-endian magic 80371240, final 16 KiB alignment, CIC-6105 header CRCs.
- BPS reconstructs the complete tested target from the original USA source.
- Native save cold boot and fresh exact-ROM state if a new profile is made.
- Gameplay checks appropriate to the affected native paths and ON/OFF modes.
- Clean source commit, then deterministic rebuild with the same ROM hash as the
  tested working-tree binary. If bytes differ, determine why before calling it
  the tested release; a commit ID alone is not binary evidence.

`build/n64crc.py` exposes `get_cic` and `crc` for read-only verification; `fixCRC`
mutates a ROM. `tools/make-bps.py` exposes patch application/CRC verification.
Look at the v0.4.2 artifact-checks.json for the evidence schema. Do not run an old
review packager if it will overwrite historical results.

## Checkpoint only when requested

Use the next agreed version after inspecting tags. Existing history includes the
historical `v3.1` label; retain it rather than renaming it. v0.4.2 is already saved.

1. Commit the tested change. Annotate the new version tag at its correct commit;
   never move an existing version tag or silently reset unrelated work.
2. Create a new `runtime/checkpoints/<version>/` directory, refusing to overwrite
   an existing backup. Copy the version-named ROM, verified BPS, build manifest,
   source diff, complete Git bundle, workspace-support archive, and relevant
   exact-ROM state/native save copies and test summaries.
3. `git bundle create <new-or-current-bundle-path> --all` and verify it; include
   the new tag. A bundle made before tagging does not preserve that new tag.
4. Write RESTORE.txt and checkpoint.json with version, gameplay commit, ROM hash,
   validation limits and per-file SHA-256 values; verify every copied byte/hash.
5. Keep the normal launcher pointed to the intended build and preserve the
   user's native progress/controls in its separate profile. Create a fresh slot 5
   if useful, using native gameplay rather than importing old-ROM RAM/code.
6. Update workspace KRUSHA.md/current validation index and refresh **current**
   support backups if needed. Frozen checkpoints and past reviews stay intact.

The root tools/docs are outside the Git repo. Keep public knowledge in the
tracked handoff/docs; workspace-support.tar.gz preserves selected parent files
for local recovery. Do not include private ROMs, EEPROM or machine-specific
paths as public release assets. Source .gitignore intentionally excludes ROMs,
BPS, symbols and object output; release patches are separate artifacts.

The user intends to publish to their GitHub later. Prepare reviewable local
changes within the current request. This playbook does not authorize a network
push, repository creation or public release by itself.

## Recover without disturbing live work

Read a checkpoint's RESTORE.txt and checkpoint.json first. Verify hashes.
Prefer a separate checkout/worktree or clone from source.bundle to inspect old
source. Use its ROM and matching state together in an isolated profile. A tag,
file name, or loading a stale state does not prove that an emulator executed the
expected ROM. Keep current user saves and working-tree edits intact.
