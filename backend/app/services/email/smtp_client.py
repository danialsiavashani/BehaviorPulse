import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.services.email.base import EmailClient


class SMTPEmailClient(EmailClient):
    def __init__(self, host: str, port: int, username: str, password: str, from_email: str):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Reset your BehaviorPulse password"
        message["From"] = self._from_email
        message["To"] = to_email

        text_body = (
            "We received a request to reset your BehaviorPulse password.\n\n"
            f"Reset it here: {reset_link}\n\n"
            "This link expires in 30 minutes. If you didn't request this, "
            "you can safely ignore this email."
        )
        html_body = f"""
        <p>We received a request to reset your BehaviorPulse password.</p>
        <p><a href="{reset_link}">Reset your password</a></p>
        <p>This link expires in 30 minutes. If you didn't request this, you can safely ignore this email.</p>
        """

        message.attach(MIMEText(text_body, "plain"))
        message.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self._host, self._port, timeout=10) as server:
            server.starttls()
            server.login(self._username, self._password)
            server.sendmail(self._from_email, to_email, message.as_string())