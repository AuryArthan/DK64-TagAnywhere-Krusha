# Start here: DK64 Krusha project handoff

Written 2026-10-31, updated 2026-11-01 for a fresh AI session. This is a navigation guide and a dated
knowledge snapshot, not a new request to change the game. Read the user's latest
request first. Inspect the actual checkout before acting on this snapshot.

## Five-minute orientation

1. Read [CURRENT_STATE.md](CURRENT_STATE.md): accepted release, hashes, user intent.
2. Run `python3 codex_handoff/verify_environment.py` from the repository (or use
   `python3 dk64-tag-anywhere/codex_handoff/verify_environment.py` from the workspace).
   This only reads files and Git status. Differences may be legitimate later work;
   investigate them rather than restoring this snapshot automatically.
3. Read the repository [README](../README.md) for current features and limitations.
4. Read [WORKSPACE.md](WORKSPACE.md) to locate the real Git repository, pinned tools,
   ROMs, checkpoints, screenshots and the reverse-engineering references.
5. Read [the maintained tools guide](../tools/README.md); tools now live inside
   the repo. Older workspace commands in historical notes are not the active layout.
6. For implementation work, load [ENGINE_MAP.md](ENGINE_MAP.md) and the relevant
   linked source/document. For gameplay tests, read [playbooks/TESTING.md](playbooks/TESTING.md)
   **before launching any test script**.

The latest approved checkpoint is **v0.6**, with 249 assertions on its exact ROM.
Its BPS, annotated tag and release-on-push workflow are prepared locally; hosted
publication requires the user to push the tag and branch. v0.5 and earlier
checkpoints remain preserved. Read CURRENT_STATE for hashes, scope and limits;
continue the latest authorized request rather than an old experiment.

## Find the right kind of knowledge

| Need | Read |
| --- | --- |
| Current decisions and release identity | [CURRENT_STATE](CURRENT_STATE.md) |
| Workspace versus a standalone Git clone | [WORKSPACE](WORKSPACE.md) |
| C/ASM/assets and useful USA RAM addresses | [ENGINE_MAP](ENGINE_MAP.md) |
| Reproduce gameplay, use the controller, interpret results | [Testing playbook](playbooks/TESTING.md) |
| Mupen64Plus-Next input, native saves and QA pitfalls | [Libretro playbook](playbooks/LIBRETRO.md) |
| Build, validate and preserve a requested checkpoint | [Build/release playbook](playbooks/BUILD_AND_CHECKPOINT.md) |
| Things already tried, harness failures and design boundaries | [PITFALLS_AND_DECISIONS](PITFALLS_AND_DECISIONS.md) |
| Milestone history | [Changelog](../docs/CHANGELOG.md) |
| Small copied evidence summaries | [snapshot.json](snapshot.json) |

The playbooks are project-specific reusable procedures. They do not depend on
an installed Codex skill, a particular chat history, or a particular tool API.
A later agent can use its available shell/exec tools to follow them. Paths in
the handoff are relative unless explicitly labeled as the original machine path.

## Source of truth and maintenance

Use current source and actual ROM hashes first. A report proves only the ROM
hash it records. Historical technical notes contain abandoned implementations;
read their final revisions and the live source before copying an idea. Earlier
`EMULATOR.md` statements about what was not yet tested describe the initial
vanilla-game setup, not the latest Krusha release.

After substantial future work, update CURRENT_STATE, this snapshot's metadata,
and relevant playbooks with actual evidence. Keep old release tags, backups and
raw reports intact. Commit the knowledge with the implementation/documentation;
never include a private ROM or a live EEPROM save in the public handoff.

## Prompt to paste into a new session

> This is the DK64 Krusha + Tag Anywhere project. Read
> `codex_handoff/README.md` and `codex_handoff/CURRENT_STATE.md`, run the read-only
> status checker, then inspect Git status. Load the linked testing/engine notes
> as needed. Summarize the actual current state and continue my latest request.
> Preserve release checkpoints and my saves; use isolated profiles for tests.
