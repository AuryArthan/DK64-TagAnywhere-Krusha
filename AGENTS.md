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

In the full development workspace, the Git repo is `dk64-tag-anywhere/` and
parent `tools/`, `runtime/`, and the private source ROM are outside it. In a
standalone clone, use `docs/BUILDING.md`; do not assume those parent files exist.
