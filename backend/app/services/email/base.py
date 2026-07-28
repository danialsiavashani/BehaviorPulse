from abc import ABC, abstractmethod


class EmailClient(ABC):
    """Abstract interface every email-sending provider must implement.

    The rest of the app only ever depends on this interface, never on a
    specific provider's SDK - swapping Gmail SMTP for a transactional email
    API later means writing one new class here, not touching any calling
    code.
    """

    @abstractmethod
    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """Sends a password-reset email containing the given link.

        Implementations should raise on failure rather than fail silently -
        the caller decides how to handle a send failure, not this layer.
        """
        raise NotImplementedError