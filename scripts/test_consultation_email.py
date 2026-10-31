#!/usr/bin/env python3
"""Send ONE clearly labeled test email through the website's current SMTP.

Run on yeet from ~/reboot-syndicate:
    git show origin/main:scripts/test_consultation_email.py > /tmp/test_consultation_email.py
    python3 /tmp/test_consultation_email.py

Does not submit a fake lead or change the customer SQLite database.
Never prints login credentials or customer details.
"""
from pathlib import Path
import subprocess
import sys

if not Path("docker-compose.yml").is_file():
    sys.exit("ERROR: Run inside ~/reboot-syndicate on yeet.")

test_code = r"""
import os
import smtplib
import ssl
from email.message import EmailMessage

receiver=os.getenv('NOTIFY_TO','').strip()
sender=os.getenv('SMTP_USERNAME','').strip()
password=os.getenv('SMTP_APP_PASSWORD','').replace(' ','').strip()
if not receiver or not sender or not password:
    raise SystemExit('ERROR: Email destination or SMTP login is not configured in the website container.')

mail=EmailMessage()
mail['Subject']='[Reboot Syndicate] TEST - Consultation email notifications'
mail['From']=sender
mail['To']=receiver
mail.set_content(
    'This is a TEST of your Reboot Syndicate consultation email notification system.\n'
    'No customer request was submitted or added to the website database.\n'
    'Future real inquiries will contain the customer contact and project details.\n'
)

try:
    host=os.getenv('SMTP_HOST','smtp.gmail.com').strip()
    port=int(os.getenv('SMTP_PORT','465'))
    with smtplib.SMTP_SSL(host,port,timeout=15,context=ssl.create_default_context()) as smtp:
        smtp.login(sender,password)
        smtp.send_message(mail)
except (OSError,smtplib.SMTPException,ValueError) as error:
    raise SystemExit('ERROR: SMTP test failed ('+type(error).__name__+'). Check Gmail App Password and network access.')
print('PASS: Test notification accepted by SMTP for delivery to '+receiver)
"""

result=subprocess.run(
    ["docker","compose","exec","-T","website","python","-c",test_code],
    text=True,capture_output=True
)
if result.stdout:
    print(result.stdout.strip())
if result.returncode:
    print(result.stderr.strip()[:700])
    sys.exit(1)
print("Check the destination inbox, including Spam, for the TEST subject.")
