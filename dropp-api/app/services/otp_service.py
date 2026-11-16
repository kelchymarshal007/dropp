import os
import random
import string
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

# In-memory stores. Replace with Redis before horizontal scaling.
_email_otp_store: dict = {}
_phone_otp_store: dict = {}


def _gen6() -> str:
    return ''.join(random.choices(string.digits, k=6))


# ---------------- EMAIL ----------------

def _send_smtp(to_email: str, code: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    frm = os.getenv("SMTP_FROM", user or "no-reply@dropp.app")

    if not (host and user and pwd):
        print(f"\n===== MOCK EMAIL =====\nTO: {to_email}\nCODE: {code}\n======================\n")
        return

    msg = MIMEMultipart()
    msg["From"] = frm
    msg["To"] = to_email
    msg["Subject"] = "Your Dropp verification code"
    msg.attach(MIMEText(f"Your Dropp verification code is: {code}\n\nExpires in 10 minutes.", "plain"))

    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, pwd)
        s.send_message(msg)


async def send_email_otp(email: str) -> str:
    code = _gen6()
    _email_otp_store[email.lower()] = code
    await asyncio.to_thread(_send_smtp, email, code)
    return code


def verify_email_otp(email: str, code: str) -> bool:
    stored = _email_otp_store.get(email.lower())
    if stored and stored == code:
        del _email_otp_store[email.lower()]
        return True
    return False


# ---------------- PHONE (Termii) ----------------

def _send_termii(phone: str, code: str) -> None:
    api_key = os.getenv("TERMII_API_KEY")
    sender = os.getenv("TERMII_SENDER_ID", "Dropp")

    if not api_key:
        print(f"\n===== MOCK SMS =====\nTO: {phone}\nCODE: {code}\n====================\n")
        return

    try:
        resp = requests.post(
            "https://api.ng.termii.com/api/sms/send",
            json={
                "to": phone,
                "from": sender,
                "sms": f"Your Dropp verification code is: {code}",
                "type": "plain",
                "channel": "generic",
                "api_key": api_key,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"Termii error: {resp.status_code} {resp.text}")
            print(f"Fallback MOCK SMS TO {phone}: {code}")
    except Exception as e:
        print(f"Termii request failed: {e}")
        print(f"Fallback MOCK SMS TO {phone}: {code}")


async def send_phone_otp(phone_e164: str) -> str:
    code = _gen6()
    _phone_otp_store[phone_e164] = code
    await asyncio.to_thread(_send_termii, phone_e164, code)
    return code


def verify_phone_otp(phone_e164: str, code: str) -> bool:
    stored = _phone_otp_store.get(phone_e164)
    if stored and stored == code:
        del _phone_otp_store[phone_e164]
        return True
    return False
