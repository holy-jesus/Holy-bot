import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate
from pathlib import Path

SMTP_SERVER = os.getenv("EMAIL_SERVER")
SMTP_PORT = 587
USERNAME = os.getenv("EMAIL_FROM")
PASSWORD = os.getenv("EMAIL_PASSWORD")

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _load_template(template_name: str, code: str) -> str:
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        return f"Ваш код: {code}"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content.replace("{code}", code)


def _send_email(to_email: str, subject: str, html_content: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"HolyBot <{USERNAME}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Message-ID"] = make_msgid(domain="holy-bot.ru")
        msg["Date"] = formatdate(localtime=True)

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.sendmail(USERNAME, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def send_email(email: str, subject: str, html_content: str) -> bool:
    return await asyncio.to_thread(_send_email, email, subject, html_content)


async def send_verification_code(email: str, verification_code: str) -> bool:
    html = _load_template("verification.html", verification_code)
    return await send_email(email, "Код подтверждения регистрации", html)


async def send_password_reset_code(email: str, verification_code: str) -> bool:
    html = _load_template("reset.html", verification_code)
    return await send_email(email, "Код подтверждения сброса пароля", html)


async def send_login_code(email: str, verification_code: str) -> bool:
    html = _load_template("login.html", verification_code)
    return await send_email(email, "Код подтверждения входа", html)
