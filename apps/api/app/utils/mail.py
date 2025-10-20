from email.message import EmailMessage
import smtplib
from string import Template
from pathlib import Path
from typing import Dict, Any

from ..core.config import get_settings

TEMPLATE_DIR = Path(__file__).resolve().parent / 'templates'


def render_template(name: str, context: Dict[str, Any]) -> str:
  template_path = TEMPLATE_DIR / name
  content = template_path.read_text()
  return Template(content).safe_substitute(**context)


def send_templated_email(*, to: str, subject: str, template: str, context: Dict[str, Any]) -> None:
  settings = get_settings()
  body = render_template(template, context)
  msg = EmailMessage()
  msg["Subject"] = subject
  msg["From"] = settings.default_admin_email
  msg["To"] = to
  msg.set_content(body, subtype="html")
  with smtplib.SMTP(settings.mailhog_host, settings.mailhog_port) as smtp:
    smtp.send_message(msg)
