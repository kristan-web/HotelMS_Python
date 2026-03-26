"""
OTP & Email Utility
====================
Generates a 6-digit OTP and sends it via SMTP (Gmail example).

Configuration:
    Set SENDER_EMAIL and SENDER_PASSWORD below, or load from environment
    variables for better security.

Usage:
    from utils.otp_utils import generate_otp, send_otp_email
    otp = generate_otp()
    sent = send_otp_email("recipient@example.com", otp)
"""

import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── SMTP settings — change these or use environment variables ─────────────────
SENDER_EMAIL    = os.getenv("HOTEL_EMAIL",    "your_email@gmail.com")
SENDER_PASSWORD = os.getenv("HOTEL_EMAIL_PWD", "your_app_password")
SMTP_HOST       = "smtp.gmail.com"
SMTP_PORT       = 587


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of the given length."""
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_email(recipient_email: str, otp: str) -> bool:
    """
    Send the OTP to recipient_email via SMTP.
    Returns True on success, False on failure.
    """
    subject = "Hotel MS — Password Reset OTP"
    body = (
        f"Your one-time password (OTP) for Hotel MS is:\n\n"
        f"    {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you did not request this, please ignore this email."
    )

    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"[OTP] Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"[OTP] Failed to send email: {e}")
        return False