from mailgun.client import Client  # type: ignore

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)
key = settings.MAILGUN_API_KEY
domain = settings.MAILGUN_DOMAIN
client: Client = Client(auth=("api", key))


def post_message(email_to: str, subject: str, html: str) -> None:
    data = {
        "from": "Allivents <postmaster@mail.allivents.com>",
        "to": email_to,
        "subject": subject,
        "html": html,
    }

    req = client.messages.create(data=data, domain=domain)
    logger.info(req.json())
