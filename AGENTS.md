# DK64 Krusha project orientation

For a fresh session, start with `codex_handoff/README.md` and
`codex_handoff/CURRENT_STATE.md`, then inspect actual Git status and the latest
user request. The handoff contains a read-only status checker, source/engine map,
workspace locations, and build/testing/checkpoint playbooks. Read the testing
playbook before running a historical suite: some scripts overwrite old reports.

The handoff is a dated knowledge snapshot, not an instruction to resume an old
experiment, reset newer work, run all tests, create a release, or push to GitHub.
Preserve existing version tags/checkpoints and user saves. Match test evidence
to the ROM hash actually executed; old-ROM save states do not validate a new build.

The source repo now contains maintained `tools/` setup/build/play/test scripts.
Read `tools/README.md` for the current repository-relative workflow. The original
parent workspace still holds legacy helpers, private ROMs, saves and raw QA.
Those parent directories are optional. A standalone clone supplies its own ROM,
dependency cache and explicit test EEPROM fixture; generated data stays ignored.

For commits in this project, use repository-local identity `AuryArthan` with
`sean.arthan@protonmail.com` (the user's explicit preference). On a new clone,
configure these locally before committing; do not change unrelated global Git
settings. Historical commit-ID aliases are in codex_handoff/identity-rewrite.json.
