from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional

from loguru import logger

from app.utils.config import SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER


def send_email(
    to_addresses: List[str], 
    subject: str, 
    html_body: str, 
    text_body: str | None = None,
    attachment_data: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
    attachment_content_type: str = "text/calendar"
) -> None:
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP not configured; printing email to logs")
        logger.info(f"TO: {to_addresses}\nSUBJECT: {subject}\nBODY: {html_body}")
        if attachment_data:
            logger.info(f"ATTACHMENT: {attachment_filename} ({len(attachment_data)} bytes)")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = ", ".join(to_addresses)

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Add attachment if provided
        if attachment_data and attachment_filename:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename= "{attachment_filename}"',
            )
            part.add_header("Content-Type", attachment_content_type)
            msg.attach(part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_addresses, msg.as_string())
        logger.info(f"Email sent successfully to {to_addresses}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise  # Re-raise to let caller handle it
