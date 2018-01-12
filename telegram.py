from telethon.tl.types import UpdateShortMessage

from logging_utils import get_module_logger
from notify import notify

logger = get_module_logger(__name__)


def handle_message(update):
    logger.info("Got new update: %s", update)

    if isinstance(update, UpdateShortMessage):
        notify(update.message, update.user_id)
