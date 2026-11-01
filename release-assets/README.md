# Patch release on push

`v0.6.1/DK64-TagAnywhere+Krusha.bps` is the verified patch copied from the approved
checkpoint, not a ROM. It is deliberately tracked despite the general BPS ignore
rule. Its SHA-256 is pinned in `tools/publish-v061.py`.

Push the existing v0.6.1 tag, then the current branch:

```sh
git push origin refs/tags/v0.6.1
git push origin HEAD
```

This publishes only after those local commits reach GitHub. The dedicated workflow
runs when these release files or its publisher change. It can also be started
from Actions → Publish v0.6.1 BPS → Run workflow on the default branch.
GitHub's automatic workflow token supplies `contents: write`; no personal token
is committed. Uploading requires Actions to be enabled and repository policy to
permit that write permission. The publisher is scoped to this specific repository.

The script verifies the approved tag and patch, creates a draft, attaches only
the BPS, checks the returned name/size/digest where supplied, and publishes the
release as latest. Existing differing assets are left untouched. It never uploads
ROMs, saves, support bundles or the workspace ZIP. GitHub additionally provides
its automatic source archives on release pages.

GitHub's REST upload API can normalize special characters in names. The publisher
requests the exact plus sign and tries the asset-name update API if necessary.
If GitHub still changes it, the workflow fails with the new release left as a
draft: use Edit release in the webpage to upload the exact filename and publish.
See https://github.com/github/rest-api-description/issues/2968 for that API/web
filename distinction. No successful hosted run has been claimed from local tests.

The workflow does not change repository visibility. Make the repository public
through GitHub settings if anonymous downloads and public source are desired.

Local checks (no network writes):

```sh
python3 tools/publish-v061.py --check-only
python3 tools/test-publish-v061.py
```

Expected version-specific download after successful publication:
`https://github.com/AuryArthan/DK64-TagAnywhere-Krusha/releases/download/v0.6.1/DK64-TagAnywhere%2BKrusha.bps`

For later versions, prepare and verify a new patch/tag and deliberately update
the publisher/workflow. This workflow only publishes the specifically requested
v0.6.1, not every build or tag in the repository.

Historical v0.6, v0.5 and v0.4.2 assets, tags and publishers/workflows are preserved unchanged.
