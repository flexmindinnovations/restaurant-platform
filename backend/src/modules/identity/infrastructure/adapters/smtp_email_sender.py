import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from modules.identity.application.ports.email_sender import EmailSender

logger = structlog.get_logger()


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 1025,
        from_email: str = "noreply@restaurantplatform.com",
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._from_email = from_email

    async def send_verification_email(self, email: str, token: str) -> None:
        subject = "Verify Your Account"
        body = f"Please verify your account using this token: {token}"
        await self._send_email(email, subject, body)

    async def send_password_reset_email(self, email: str, token: str) -> None:
        subject = "Reset Your Password"
        body = f"Please reset your password using this token: {token}"
        await self._send_email(email, subject, body)

    async def _send_email(self, to_email: str, subject: str, body: str) -> None:
        logger.info("sending_email", to=to_email, subject=subject)
        try:
            msg = self._build_message(to_email, subject, body)
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.sendmail(self._from_email, to_email, msg.as_string())
            logger.info("email_sent_successfully", to=to_email)
        except Exception as e:
            logger.exception("email_send_failed", to=to_email, error=str(e))

    def _build_message(self, to_email: str, subject: str, body: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["From"] = self._from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        return msg
