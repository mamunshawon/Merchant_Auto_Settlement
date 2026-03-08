import mimetypes
import os
import re
import smtplib
from email.message import EmailMessage

from utils.logger import get_logger

logger = get_logger("EMAIL")


def _parse_recipients(value: str) -> list[str]:
    if not value:
        return []
    parts = [p.strip() for p in re.split(r"[\s,]+", value) if p.strip()]
    # De-dup while preserving order
    seen: set[str] = set()
    recipients: list[str] = []
    for p in parts:
        if p not in seen:
            recipients.append(p)
            seen.add(p)
    return recipients


class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int, sender: str, receiver: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.receiver_raw = receiver

    def send_report(self, report_path: str, subject: str, body: str) -> None:
        self.send_reports([report_path], subject=subject, body=body)

    def send_reports(self, report_paths: list[str], subject: str, body: str) -> None:
        recipients = _parse_recipients(self.receiver_raw)
        if not recipients:
            raise ValueError("No email recipients configured (EMAIL_RECEIVER is empty)")

        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body)

        for report_path in report_paths:
            report_path = os.path.abspath(report_path)
            if not os.path.exists(report_path):
                raise FileNotFoundError(f"Report file not found: {report_path}")

            ctype, encoding = mimetypes.guess_type(report_path)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)

            with open(report_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(report_path),
                )

        logger.info(
            f"Sending report email via {self.smtp_server}:{self.smtp_port} to {recipients}"
        )
        with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as smtp:
            smtp.send_message(msg)
        logger.info("Report email sent successfully")

