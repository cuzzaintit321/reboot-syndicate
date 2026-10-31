#!/usr/bin/env python3
"""Update the destination for Reboot Syndicate consultation emails.

Run from ~/reboot-syndicate after fetching the latest GitHub version:
    python3 /tmp/set_consultation_email.py aintit321@gmail.com

Preserves SQLite leads, SMTP credentials, forms, images, and website design.
Private config backups are kept outside the Git repository.
"""
import argparse
from datetime import datetime
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("recipient", help="Gmail or other email inbox for form alerts")
args = parser.parse_args()
recipient = args.recipient.strip()

if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_{}|~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", recipient):
    sys.exit("ERROR: Recipient is not a valid email address.")

ROOT = Path.cwd()
ENV = ROOT / ".env"
COMPOSE = ROOT / "docker-compose.yml"
APP = ROOT / "app/notifications.py"
if not COMPOSE.is_file() or not APP.is_file():
    sys.exit("ERROR: Run inside ~/reboot-syndicate on yeet.")
if "NOTIFY_TO" not in APP.read_text(encoding="utf-8"):
    sys.exit("ERROR: Website notification code doesn't support NOTIFY_TO.")
if os.environ.get("NOTIFY_TO") and os.environ["NOTIFY_TO"] != recipient:
    sys.exit("ERROR: Shell NOTIFY_TO overrides .env. Unset it before running this script.")

env_before = ENV.read_text(encoding="utf-8") if ENV.is_file() else ""
env_lines = env_before.splitlines(keepends=True)
new_lines = []
found = False
for line in env_lines:
    if re.match(r"^\s*(?:export\s+)?NOTIFY_TO\s*=", line):
        if not found:
            new_lines.append("NOTIFY_TO=" + recipient + "\n")
            found = True
    else:
        new_lines.append(line)
if not found:
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"
    new_lines.append("NOTIFY_TO=" + recipient + "\n")
env_after = "".join(new_lines)

# Add environment forwarding to website service only; keep all existing
# Compose content, container names, port mappings, and data volumes.
compose_before = COMPOSE.read_text(encoding="utf-8")
match = re.search(r"(?m)^  website:\s*$", compose_before)
if not match:
    sys.exit("ERROR: Website service missing in Docker Compose.")
a = match.end()
next_service = re.search(r"(?m)^  [A-Za-z_][A-Za-z0-9_-]*:\s*$", compose_before[a:])
b = a + next_service.start() if next_service else len(compose_before)
section = compose_before[a:b]
environment = re.search(r"(?m)^    environment:\s*$", section)
variables = ("NOTIFY_TO", "SMTP_USERNAME", "SMTP_APP_PASSWORD")

def compose_variable(name):
    return "$" + "{" + name + ":-}"

if environment:
    start = environment.end()
    next_field = re.search(r"(?m)^    [A-Za-z_][A-Za-z0-9_-]*:\s*", section[start:])
    end = start + next_field.start() if next_field else len(section)
    block = section[start:end]
    is_list = bool(re.search(r"(?m)^      -\s+", block))
    is_map = bool(re.search(r"(?m)^      [A-Za-z_][A-Za-z0-9_-]*\s*:", block))
    if not (is_list or is_map or not block.strip()) or (is_list and is_map):
        sys.exit("ERROR: Unsupported website environment format. No changes made.")
    if not is_map:
        for name in variables:
            pattern = re.compile(r"(?m)^      -\s+" + name + r"(?:=.*)?$")
            line = "      - " + name + "=" + compose_variable(name)
            if pattern.search(block):
                if name == "NOTIFY_TO":
                    block = pattern.sub(line, block, count=1)
            else:
                block = block.rstrip("\n") + "\n" + line + "\n"
    else:
        for name in variables:
            pattern = re.compile(r"(?m)^      " + name + r":.*$")
            line = "      " + name + ": " + compose_variable(name)
            if pattern.search(block):
                if name == "NOTIFY_TO":
                    block = pattern.sub(line, block, count=1)
            else:
                block = block.rstrip("\n") + "\n" + line + "\n"
    section_after = section[:start] + block + section[end:]
else:
    block = "\n    environment:\n" + "".join(
        "      - " + name + "=" + compose_variable(name) + "\n"
        for name in variables
    )
    section_after = section[:1] + block + section[1:] if section.startswith("\n") else block + section
compose_after = compose_before[:a] + section_after + compose_before[b:]

# Validate the amended Compose file with the new .env before changing the live
# files. Never show rendered Compose configuration because it may contain secrets.
with tempfile.TemporaryDirectory(prefix="rs-email-preflight-") as directory:
    tmp = Path(directory)
    (tmp / "docker-compose.yml").write_text(compose_after, encoding="utf-8")
    (tmp / ".env").write_text(env_after, encoding="utf-8")
    test = subprocess.run(
        ["docker", "compose", "--env-file", str(tmp / ".env"),
         "-f", str(tmp / "docker-compose.yml"), "--project-directory",
         str(ROOT), "config", "--format", "json"],
        cwd=ROOT, capture_output=True, text=True
    )
    if test.returncode:
        sys.exit("ERROR: Docker Compose preflight failed; no changes made.")
    try:
        config = json.loads(test.stdout)
        if config["services"]["website"]["environment"].get("NOTIFY_TO") != recipient:
            sys.exit("ERROR: Docker Compose does not resolve the new recipient.")
    except (ValueError, KeyError, TypeError):
        sys.exit("ERROR: Cannot validate Compose environment. No changes made.")

# Keep backups OUTSIDE the repository to avoid exposing sensitive SMTP data.
backup = ROOT.parent / ".reboot-syndicate-config-backups" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
backup.mkdir(parents=True, exist_ok=False)
backup.chmod(0o700)
if ENV.is_file() and env_after != env_before:
    shutil.copy2(ENV, backup / "env.before")
    (backup / "env.before").chmod(0o600)
if compose_after != compose_before:
    shutil.copy2(COMPOSE, backup / "docker-compose.yml.before")
    (backup / "docker-compose.yml.before").chmod(0o600)
if env_after != env_before:
    ENV.write_text(env_after, encoding="utf-8")
    ENV.chmod(0o600)
if compose_after != compose_before:
    COMPOSE.write_text(compose_after, encoding="utf-8")
print("New consultation notification inbox:", recipient)
print("SMTP credentials and saved customer inquiries: untouched.")
print("Updating only the website container's environment...")
subprocess.run(["docker", "compose", "up", "-d", "--no-deps",
                "--force-recreate", "website"], cwd=ROOT, check=True)

checkcode = (
    "import os; "
    "print('NOTIFY_TO=' + os.getenv('NOTIFY_TO', '<missing>')); "
    "print('SMTP username configured=' + str(bool(os.getenv('SMTP_USERNAME')))); "
    "print('SMTP app password configured=' + str(bool(os.getenv('SMTP_APP_PASSWORD'))))"
)
check = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", checkcode],
    cwd=ROOT, text=True, capture_output=True
)
if check.returncode:
    sys.exit("ERROR: Cannot verify new environment in container.")
print(check.stdout.strip())
if ("NOTIFY_TO=" + recipient) not in check.stdout:
    sys.exit("ERROR: Container did not receive the new address.")
if "SMTP username configured=True" not in check.stdout or "SMTP app password configured=True" not in check.stdout:
    print("WARNING: Recipient updated, but SMTP login settings are missing.")
    print("Requests will still be saved in SQLite; email alerts are not active yet.")
else:
    print("PASS: Consultation notifications are addressed to " + recipient)
    print("SMTP settings found; a test email is needed to confirm delivery.")
print("Private config backups:", backup)
