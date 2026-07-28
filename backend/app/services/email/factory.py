from app.core.config import settings
from app.services.email.base import EmailClient
from app.services.email.console_client import ConsoleEmailClient
from app.services.email.smtp_client import SMTPEmailClient


def get_email_client() -> EmailClient:
    if settings.smtp_host and settings.smtp_username and settings.smtp_password and settings.smtp_from_email:
        return SMTPEmailClient(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_email=settings.smtp_from_email,
        )

    return ConsoleEmailClient()