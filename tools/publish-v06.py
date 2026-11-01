#!/usr/bin/env python3
"""Publish the approved BPS through GitHub's API. No ROM or personal token in Git."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, urllib.request, urllib.error, urllib.parse
ROOT = Path(__file__).resolve().parent.parent
REPO = 'AuryArthan/DK64-TagAnywhere-Krusha'
TAG = 'v0.6'
COMMIT = '3fc3627e09c9a581c9326e50548df3a2379783a7'
NAME = 'DK64-TagAnywhere+Krusha.bps'
SHA = '4178fc17e01fa577cc1977396db08d34b5b7507fdcc4e4207acdb0f214e8cd88'
BASE = 'https://api.github.com/repos/' + REPO


def validate():
    data = (ROOT / 'release-assets' / TAG / NAME).read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA:
        raise RuntimeError('Patch differs from the approved v0.6 checkpoint')
    target = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', TAG + '^{}'], text=True).strip()
    if target != COMMIT:
        raise RuntimeError('Push the existing approved v0.6 tag before publishing; never recreate or move it')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    data = validate()
    if args.check_only:
        print('Approved patch checksum and release tag verified. No network writes.')
        return
    if os.environ.get('GITHUB_REPOSITORY', REPO) != REPO:
        raise RuntimeError('This publisher is restricted to the requested repository')
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GitHub API authentication is required; use the release workflow')

    def api(method, url, body=None, binary=False):
        if not (url.startswith(BASE + '/') or url.startswith('https://uploads.github.com/repos/' + REPO + '/')):
            raise RuntimeError('Unexpected API destination')
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                   'User-Agent': 'DK64-v06-release', 'X-GitHub-Api-Version': '2022-11-28'}
        if body is not None:
            headers['Content-Type'] = 'application/octet-stream' if binary else 'application/json'
            if not binary:
                body = json.dumps(body).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers, method=method), timeout=120) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code == 404 and method == 'GET':
                return None
            raise RuntimeError(f'GitHub API {method} failed with HTTP {e.code}; check Actions permissions') from None

    release = api('GET', BASE + '/releases/tags/' + TAG)
    if release is None:
        release = api('POST', BASE + '/releases', {
            'tag_name': TAG, 'name': 'Krusha + Tag Anywhere v0.6', 'draft': True,
            'prerelease': False, 'body': (ROOT / 'release-assets' / TAG / 'notes.md').read_text()})
    asset = next((a for a in release['assets'] if a['name'] == NAME), None)
    if asset:
        if asset.get('digest') != 'sha256:' + SHA:
            raise RuntimeError('Existing asset cannot be verified; left untouched')
    else:
        if not release['draft']:
            raise RuntimeError('Existing published release has no matching asset; left untouched for review')
        # Never clobber existing assets. Keep a newly created release a draft on failure.
        url = release['upload_url'].split('{')[0] + '?name=' + urllib.parse.quote(NAME, safe='')
        asset = api('POST', url, data, binary=True)
        if asset['name'] != NAME:
            asset = api('PATCH', BASE + '/releases/assets/' + str(asset['id']), {'name': NAME})
        if asset['name'] != NAME:
            raise RuntimeError('GitHub normalized the plus sign; upload the exact filename through the Releases webpage. Draft was not published.')
        if asset['size'] != len(data) or asset.get('digest') not in (None, 'sha256:' + SHA):
            raise RuntimeError('Uploaded patch verification failed; draft was not published')
    if release['draft']:
        release = api('PATCH', BASE + '/releases/' + str(release['id']), {'draft': False, 'make_latest': 'true'})
    print('Release:', release['html_url'])
    print('Patch:', asset['browser_download_url'])


if __name__ == '__main__':
    main()
