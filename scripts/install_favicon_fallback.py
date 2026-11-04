#!/usr/bin/env python3
"""Add a root favicon fallback using the existing Reboot Syndicate icon."""
from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

MOUNT = "app.mount('/static', StaticFiles(directory='app/static'), name='static')"
ROUTE = """
@app.api_route('/favicon.ico', methods=['GET', 'HEAD'], include_in_schema=False)
def favicon():
    from fastapi.responses import FileResponse
    return FileResponse(Path(__file__).resolve().parent / 'static/favicon.ico', media_type='image/x-icon')
"""
PNG_TAG = '<link rel="icon" type="image/png" sizes="192x192" href="/static/favicon-192.png">'
ICON_TAG = re.compile(r'<link\b(?=[^>]*\brel=["\'](?:icon|shortcut icon)["\'])[^>]*>', re.I)
REBUILD = ['docker', 'compose', 'up', '-d', '--no-deps', '--build', '--wait', '--wait-timeout', '90', 'website']


def source_with_icon(source):
    if ROUTE.strip() in source:
        return source
    if 'favicon.ico' in source or source.count(MOUNT) != 1:
        raise ValueError('Review the existing favicon route or static mount before installing')
    return source.replace(MOUNT, MOUNT + '\n' + ROUTE, 1)


def write_atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temp.write(data)
        name = temp.name
    try:
        os.chmod(name, path.stat().st_mode & 0o777 if path.exists() else 0o644)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def install(root, release):
    if not (root / 'docker-compose.yml').is_file():
        raise ValueError('Reboot Syndicate installation was not found')
    main = root / 'app/main.py'
    home = root / 'app/templates/index.html'
    updated = source_with_icon(main.read_text())
    compile(updated, str(main), 'exec')
    markup, count = ICON_TAG.subn(PNG_TAG, home.read_text(), count=1)
    if count != 1:
        raise ValueError('Could not identify the existing homepage favicon link')
    files = {
        main: updated.encode(),
        home: markup.encode(),
        root / 'app/static/favicon.ico': (release / 'app/static/favicon.ico').read_bytes(),
        root / 'app/static/favicon-192.png': (release / 'app/static/favicon-192.png').read_bytes(),
    }
    changes = {path: content for path, content in files.items()
               if not path.exists() or path.read_bytes() != content}
    if not changes:
        print('Favicon files are already installed.')
    backup = root / 'backups' / ('favicon-fallback-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    for path in changes:
        if path.exists():
            target = backup / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    try:
        for path, content in changes.items():
            write_atomic(path, content)
        subprocess.run(REBUILD, cwd=root, check=True)
        for route, filename in (('/favicon.ico', 'favicon.ico'), ('/static/favicon-192.png', 'favicon-192.png')):
            served = subprocess.check_output([
                'curl', '-fsS', '--max-time', '12', '--resolve', 'rebootsyndicate.com:443:127.0.0.1',
                'https://rebootsyndicate.com' + route,
            ])
            if served != files[root / 'app/static' / filename]:
                raise ValueError(f'{route} did not serve the expected icon')
    except (OSError, ValueError, subprocess.CalledProcessError, KeyboardInterrupt):
        for path in changes:
            saved = backup / path.relative_to(root)
            if saved.is_file():
                write_atomic(path, saved.read_bytes())
            else:
                path.unlink(missing_ok=True)
        if changes:
            subprocess.run(REBUILD, cwd=root, check=False)
        raise
    print('Verified the root ICO and the existing PNG through Caddy.')


if __name__ == '__main__':
    try:
        install(Path.home() / 'reboot-syndicate', Path(__file__).resolve().parents[1])
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from None
