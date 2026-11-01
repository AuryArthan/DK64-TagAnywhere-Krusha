# Workspace and evidence map

Original workspace root: `/home/rok/Dropbox/romhacking/dk64_codex`.
The root itself is **not** the game Git repository. The repo is its child
`dk64-tag-anywhere/`. Run Git with `git -C dk64-tag-anywhere ...` from the root.

The tracked handoff lives at `dk64-tag-anywhere/codex_handoff/`; a workspace-root
symlink `codex_handoff` points there. AGENTS.md pointers make it discoverable in
both a full workspace and a standalone clone.

## Maintained workflow after migration

The repo now has its own `tools/` scripts, keyboard config, dependency setup and
regression runner. Read [tools/README.md](../tools/README.md). All active paths
are repository-relative; default generated output is repo `runtime/`, ignored
by Git. `DK64_TOOL_ROOT` can reuse an external binary cache without making source
paths depend on a parent workspace. The original parent's tools/runtime remain
legacy backups and the user's existing play profiles are unchanged. The table
below describes that original workspace, not requirements for a standalone clone.

## Full workspace layout

| Location | Purpose |
| --- | --- |
| `dk64-tag-anywhere/` | Actual source repo, assets, docs, ROM output |
| `public-patch-release/` | Retired patch-only clone; do not push its obsolete history. The source repo now hosts both code and releases. |
| `tools/` | Build/emulator/control/test/package helpers; outside source repo |
| `tools/n64chain/`, `tools/build-tools/` | Pinned compiler, armips and gzip |
| `tools/emulator/` | Locally unpacked Mupen64Plus, plugins, Xvfb, xdotool |
| `Donkey Kong 64 (USA).z64` | Private, unmodified source ROM |
| `runtime/krusha/current` | Builder-maintained profile symlink; inspect its target. Launchers compute the profile from the actual ROM hash. |
| `runtime/roms/<SHA256>/` | Separate saves/config/states/screenshots per ROM |
| `runtime/checkpoints/v0.6/` | Current frozen ROM/BPS, Git bundle, source archive/diff, player save copies, QA fixtures/reports and hashes; v0.5/older backups remain intact |
| `runtime/krusha/build-manifest.json` | Identity of last built ROM; may point to gameplay commit before later docs commits |
| `runtime/krusha/dk64-krusha-adventure.bps` | Verified patch for the original USA ROM |
| `runtime/krusha/source.bundle` | Current Git-history backup; refresh after commits when useful |
| `runtime/krusha/workspace-support.tar.gz` | Snapshot of workspace helpers/docs; not a live checkout |
| `KRUSHA.md` | Detailed workspace feature notes/history; older sections are chronological |
| `EMULATOR.md`, `TAG_ANYWHERE.md` | Earlier setup and baseline notes |
| `research/krusha/` | Asset/animation/audio/hardware investigations |
| `input_files/` | User-supplied audio, including earlier revisions |

Reverse-engineering references are named exactly `dk64_decompillation/`,
`dk64_recompilled/`, and `dk64_reverse_engineered/` (spelling intentional).
These are partial references, not the current hack's build system. Recomp symbols
in `dk64_recompilled/DK64Syms/` and partial native source in
`dk64_decompillation/src/` have been especially useful. Verify against the original
ROM/disassembly before treating incomplete C or guessed structure types as facts.
Temporary `/tmp` dumps from past sessions are disposable, not authoritative assets.

## Current v0.6 evidence

Repository-relative paths:

- `docs/qa/krusha-collectibles-20261101.json`: committed summary of 249 assertions
  across 13 completed, matching-ROM reports; includes source/report hashes.
- `docs/krusha-collectibles-validation.md`: fixtures, actual coverage and limits.
- `runtime/qa/collectibles-20261101/final-build/`: private raw profiles and
  captures. Use the accepted paths from the public summary; earlier failed
  fixture attempts in the same tree are not accepted validation.
- `release-assets/v0.6/`: verified public BPS and release notes.
- The original parent workspace's `runtime/checkpoints/v0.6/` has the frozen
  backup. Player saves and QA states are separated and labeled in RESTORE.txt.

## Historical evidence (original parent workspace)

- `runtime/krusha/tree-tag-fix-review/`: v0.4.2 accepted result, comparison with
  v0.4.1, raw traces, matrix/on/off reports, vine cases, regressions, failed
  experiments, copied BPS/source archive and screenshots.
- `runtime/krusha/release-test-v0.4.1/`: historical broader QA. Its open finding
  is still correct for that older ROM, not a reason to reapply a fix to v0.4.2.
- `runtime/krusha/roar-timing-review/`: accelerated-shout investigation/fix.
- `runtime/krusha/pause-review/`, `layout-review/`, `widescreen-review/`,
  `barrel-edge-review/`: rendering investigations; read each manifest/hash.
- `runtime/krusha/barrel-portrait-review/`, `startup-logo-adjusted-review/`:
  final portrait and exact startup-pixel evidence.
- Public-facing screenshots are copied into repo `docs/screenshots/`, with
  provenance in its README. GitHub docs use those relative paths.

## Source ROM identity

USA .z64 SHA-1: `cf806ff2603640a748fca5026ded28802f1f4a50`.
SHA-256: `b6347d9f1f75d38a88d829b4f80b1acf0d93344170a5fbe9546c484dae416ce3`.
The build reads `dk64-tag-anywhere/rom/dk64.z64`. BPS applies to that clean
original, including the Tag Anywhere changes; do not stack it on another hack.

## Screenshots the user could not find

F12 writes `screenshots/donkey_kong_64-NNN.png` in the **running ROM's** profile.
The eleven captures 000–010 made on v0.4.1 are in
`runtime/roms/7f0e70d623258052ac066384fbebcefe309cbf1755245a2d231c721a174dbe68/screenshots/`.
For v0.6 the ROM-hash profile is
`runtime/roms/b933a3ec36f8e8b8cbcf8a06c4014b49625696077b7878dcb33fca1ac946f57f/`.
Look in its `screenshots/` folder under the repo or parent workspace, depending
on which launcher was used. The repo's `runtime/krusha/current` symlink also
points at that profile; inspect a parent symlink before assuming it is current.
An already-running emulator continues using its own profile after a new build.
Preserve old profiles and captures.

## Standalone clone

The repository now includes maintained build/play/control/test helpers and a
portable config template. Use [tools/README.md](../tools/README.md) and
[BUILDING.md](../docs/BUILDING.md). Supply the original ROM and tool dependencies;
regressions also need an explicit disposable native save fixture. No ROM, save,
downloaded binary or raw QA directory is committed. Old parent helper scripts
and large historical research remain outside the repo and backed up locally.
