import os
import smtplib
import random
from flask import request
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get client IP from request
def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

# Get user agent (device info)
def get_user_agent():
    return request.headers.get('User-Agent')

# Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# General email sender function
def send_email(to_email, body, subject="🔔 Notification"):
    from_email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("EMAIL_APP_PASSWORD")

    if not from_email or not password:
        raise EnvironmentError("ADMIN_EMAIL or EMAIL_APP_PASSWORD is not set in .env")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
    except smtplib.SMTPException as e:
        print(f"❌ Failed to send email: {e}")

# Specialized OTP email sender
def send_otp_email(to_email, otp):
    body = f"""
Hi,

We detected a login attempt on your admin dashboard.

🛡️ Your One-Time Password (OTP) is: {otp}
⏳ This code will expire in 3 minutes.

⚠️ If you didn’t request this, please secure your account immediately by changing your password.

Regards,  
My Portfolio Security Team
    """
    send_email(to_email, body, subject="🔐 Verify Your Identity - OTP Inside")
