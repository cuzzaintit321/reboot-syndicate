#!/usr/bin/env python3
"""Safely enable Reboot Syndicate consultation email notifications on yeet.

Run from ~/circuit-syndicate AFTER:
    git fetch origin main
    git show origin/main:scripts/install_email_alerts.py > /tmp/install_email_alerts.py
    python3 /tmp/install_email_alerts.py email-to-receive-alerts@example.com

Preserves local modifications to docker-compose.yml and app/main.py.
Credentials stay in .env, which is gitignored.
"""
from pathlib import Path
from datetime import datetime
import os
import re
import shutil
import subprocess
import sys

root = Path.cwd()
main_file = root / "app/main.py"
compose_file = root / "docker-compose.yml"
notifications_file = root / "app/notifications.py"
env_file = root / ".env"
recipient = sys.argv[1].strip() if len(sys.argv) > 1 else os.getenv("NOTIFY_TO", "").strip()
if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", recipient):
    raise SystemExit("Usage: python3 install_email_alerts.py email-to-receive-alerts@example.com")

if not main_file.is_file() or not compose_file.is_file():
    raise SystemExit("Run from ~/circuit-syndicate; main.py or docker-compose.yml is missing.")

def read_git(path):
    p = subprocess.run(["git", "show", "origin/main:" + path], cwd=root, text=True,
                       capture_output=True, check=False)
    if p.returncode:
        raise SystemExit("Fetch the latest GitHub code first: git fetch origin main. "
                         "Missing " + path)
    return p.stdout

# Fetch before modifying any files, so an unavailable GitHub version fails cleanly.
notification_source = read_git("app/notifications.py")
if "def send_consultation_alert(" not in notification_source:
    raise SystemExit("Unexpected notification helper. No changes made.")

old_main = main_file.read_text(encoding="utf-8")
new_main = old_main
if "background_tasks.add_task(send_consultation_alert" not in new_main:
    changes = [
      ("from app.marketing_services import router as marketing_router",
       "from app.marketing_services import router as marketing_router\nfrom app.notifications import send_consultation_alert"),
      ("from fastapi import FastAPI, Request, Form, HTTPException, Depends",
       "from fastapi import FastAPI, Request, Form, HTTPException, Depends, BackgroundTasks"),
      ("def submit(request: Request, name: str = Form(...),",
       "def submit(request: Request, background_tasks: BackgroundTasks, name: str = Form(...),"),
      ("    with db() as conn:\n"
       "        conn.execute('INSERT INTO requests(created_at,name,email,phone,device,issue,service_area) VALUES(?,?,?,?,?,?,?)', (datetime.now(timezone.utc).isoformat(), name, email, phone, device, issue, service_area))\n"
       "    return RedirectResponse('/thanks', status_code=303)",
       "    received_at = datetime.now(timezone.utc).isoformat()\n"
       "    with db() as conn:\n"
       "        cursor = conn.execute('INSERT INTO requests(created_at,name,email,phone,device,issue,service_area) VALUES(?,?,?,?,?,?,?)', (received_at, name, email, phone, device, issue, service_area))\n"
       "        request_id = cursor.lastrowid\n"
       "    background_tasks.add_task(send_consultation_alert, {\n"
       "        'id': request_id,\n"
       "        'created_at': received_at,\n"
       "        'name': name,\n"
       "        'email': email,\n"
       "        'phone': phone,\n"
       "        'service': device,\n"
       "        'message': issue,\n"
       "    })\n"
       "    return RedirectResponse('/thanks', status_code=303)")
    ]
    for before, after in changes:
        if before not in new_main:
            raise SystemExit("Your app/main.py differs from the expected version. "
                             "No changes made; missing: " + before[:85])
        new_main = new_main.replace(before, after, 1)

old_compose = compose_file.read_text(encoding="utf-8")
new_compose = old_compose
env_lines = [
    "      - NOTIFY_TO=" + "$" + "{NOTIFY_TO:-}",
    "      - SMTP_USERNAME=" + "$" + "{SMTP_USERNAME:-}",
    "      - SMTP_APP_PASSWORD=" + "$" + "{SMTP_APP_PASSWORD:-}",
    "      - SMTP_HOST=" + "$" + "{SMTP_HOST:-smtp.gmail.com}",
    "      - SMTP_PORT=" + "$" + "{SMTP_PORT:-465}",
]
missing = [line for line in env_lines if line.split("=")[0].strip() not in new_compose]
if missing:
    anchor = "    environment:\n"
    if anchor not in new_compose:
        raise SystemExit("Cannot find website environment block in docker-compose.yml. "
                         "No changes made.")
    new_compose = new_compose.replace(anchor, anchor + "\n".join(missing) + "\n", 1)

old_env = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
new_env = old_env
def set_env(key, value, replace=False):
    global new_env
    line = key + "=" + value
    pattern = r"(?m)^" + re.escape(key) + r"=.*$"
    if re.search(pattern, new_env):
        if replace:
            new_env = re.sub(pattern, lambda m: line, new_env, count=1)
    else:
        new_env += ("" if not new_env or new_env.endswith("\n") else "\n") + line + "\n"

set_env("NOTIFY_TO", recipient, replace=True)
set_env("SMTP_USERNAME", recipient)
set_env("SMTP_APP_PASSWORD", "")
set_env("SMTP_HOST", "smtp.gmail.com")
set_env("SMTP_PORT", "465")

# Take copies only when there is a change; don't overwrite live data or Docker volumes.
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = root / "backups" / ("email-notifications-" + stamp)
changes = [
    (main_file, old_main, new_main),
    (compose_file, old_compose, new_compose),
    (notifications_file, notifications_file.read_text(encoding="utf-8")
     if notifications_file.exists() else None, notification_source),
    (env_file, old_env if env_file.exists() else None, new_env),
]
for path, before, after in changes:
    if before == after:
        print("Already current:", path.relative_to(root))
        continue
    if before is not None:
        out = backup / path.relative_to(root)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)
        if path == env_file:
            os.chmod(out, 0o600)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(after, encoding="utf-8")
    if path == env_file:
        os.chmod(path, 0o600)
    print("Updated:", path.relative_to(root))

# Check for syntax before suggesting a rebuild.
import ast
ast.parse(main_file.read_text(encoding="utf-8"), filename=str(main_file))
ast.parse(notifications_file.read_text(encoding="utf-8"), filename=str(notifications_file))
print("\nRecipient configured:", recipient)
print("Existing stored requests and Docker volumes remain untouched.")
print("Next: edit .env and set SMTP_APP_PASSWORD to a Google App Password.")
print("Then: docker compose config --quiet && docker compose up -d --build website")
