from telethon.tl.types import UpdateShortMessage, UpdateNewChannelMessage

from logging_utils import get_module_logger
from notify import notify

logger = get_module_logger(__name__)


def handle_message(update):
    logger.info("Got new update: %s", update)

    if isinstance(update, UpdateShortMessage):
        notify(update.message, update.user_id)

    if isinstance(update, UpdateNewChannelMessage):
        channel_id = update.message.to_id.channel_id
        message = update.message.message
        notify(message, channel_id)
