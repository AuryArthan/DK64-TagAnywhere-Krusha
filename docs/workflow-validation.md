# Repository workflow migration validation — 2026-10-31

The maintained build, dependency setup, play/controller and selected regression
scripts now live in `tools/`. They use this repository as their source root.
The game ROM remains byte-identical to accepted v0.4.2:

`dee2bbfcd04ba4ad1c0671e3f1ddd6d212ed1c94af0476caf12d9e862144d29d`

Verification performed:

- Repository-local build wrapper produced the exact accepted ROM and verified
  its BPS reconstruction, manifest and profile selection.
- GNU gzip 1.2.4 was downloaded with SHA-256 verification and compiled from source;
  rebuilding with this executable also produced the exact accepted ROM.
- The new build-tools setup completed against the existing pinned binary/source
  cache, including archive verification and armips build steps.
- An independent Git clone in a path containing spaces built the identical ROM,
  using an explicit external tool cache. It launched the headless emulator and
  read native RDRAM status successfully. Generated files left its Git tree clean.
- **140 controller-driven assertions passed** using the migrated scripts:
  core 34, extra 10, barrel 11, gun/model 20, barrel-extra 36, options 29.
  These cover ordinary gameplay, pickups, camera/shout, shops, boulders/swimming,
  every barrel selection, native weapons and settings persistence across restarts.
- Python/shell syntax, documentation links and ignored ROM/save/runtime/cache/
  object paths were checked. No user saves or old frozen QA reports were modified.

Tests used a deliberately copied, explicitly supplied Speed Mode native EEPROM
fixture, never a save committed to Git. Runtime output is ignored under
`runtime/workflow-migration-qa/` and clone evidence is in
`runtime/workflow-migration-clone.json` in the development checkout. The original
full v0.4.2 723-assertion validation is separate historical evidence for the same
ROM; these counts should not be presented as a new full campaign certification.

The full APT-based dependency installation on a newly provisioned OS was not
repeated. Tests reused the known local compiler/emulator cache through
DK64_TOOL_ROOT, while the pinned gzip was independently rebuilt. APT resolves
host-specific package versions; replacing the core requires revalidating the
build-specific memory diagnostic offsets. Linux x86-64 is the tested workflow;
physical N64 and a fresh Windows setup remain untested.

Legacy parent-workspace launchers and archives remain available. The source
repository's tools are the maintained implementation; see tools/README.md and
the updated codex_handoff entry points. The accepted v0.4.2 tag is unchanged.
