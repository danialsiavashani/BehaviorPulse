import logging

from app.services.email.base import EmailClient

logger = logging.getLogger("signaltally")


class ConsoleEmailClient(EmailClient):
    """Used when SMTP isn't configured. Logs the reset link instead of
    sending it - lets the forgot-password flow work end to end (for local
    dev, testing, or anyone cloning this repo without setting up email)
    without ever silently failing.
    """

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        logger.info("Password reset requested for %s. Reset link: %s", to_email, reset_link)