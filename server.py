from os import environ
from flask import Flask, request, render_template, redirect
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import time
import threading

from logging_utils import get_module_logger
from notify import notify
from telegram import handle_message

import states

logger = get_module_logger(__name__)

SESSION_NAME = environ.get('TG_SESSION_NAME')
API_ID = environ.get('TG_API_ID')
API_HASH = environ.get('TG_API_HASH')
PHONE = environ.get('TG_PHONE')
IPN_URL = environ.get('TG_IPN_URL')
IPN_SECRET = environ.get('TG_IPN_SECRET')

APP = Flask(__name__)
CLIENT = TelegramClient(SESSION_NAME, API_ID, API_HASH,
                        proxy=None, update_workers=4)

CURRENT_STATE = states.STATE_INIT


@APP.errorhandler(Exception)
def handle_invalid_usage(exception):
    return str(exception), 500


@APP.route('/', methods=['GET'])
def index():
    templates = {
        states.STATE_WAIT_CODE: 'wait_code.html',
        states.STATE_WAIT_PASSWORD: 'wait_password.html',
        states.STATE_READY: 'ready.html',
        states.STATE_WAIT_SECONDS: 'wait.html',
    }

    if CURRENT_STATE in templates:
        return render_template(templates[CURRENT_STATE])

    return render_template('init.html')


@APP.route('/', methods=['POST'])
def index_post():
    global CURRENT_STATE

    logger.info('Got POST message')

    if CURRENT_STATE == states.STATE_WAIT_CODE:
        form = request.form
        try:
            logger.info('Signing with code %s...', form['code'])
            if CLIENT.sign_in(PHONE, form['code']):
                logger.info("OK")
                CURRENT_STATE = states.STATE_READY
        except SessionPasswordNeededError:
            logger.info('Password needed')
            CURRENT_STATE = states.STATE_WAIT_PASSWORD

    if CURRENT_STATE == states.STATE_WAIT_PASSWORD:
        form = request.form
        logger.info('Signing with password...')
        if CLIENT.sign_in(password=form['password']):
            logger.info("OK")
            CURRENT_STATE = states.STATE_READY

    return redirect('/')


def send_code():
    try:
        logger.info("Sending code to %s...", PHONE)
        CLIENT.send_code_request(PHONE)
    except FloodWaitError as exception:
        logger.info(
            "Flood error occured. Waiting %d seconds...", exception.seconds)
        time.sleep(exception.seconds)
        send_code()


def start_server():
    logger.info("Staring web server...")
    APP.run(host="0.0.0.0")


def connect_client():
    global CURRENT_STATE

    logger.info("Connecting telegram client...")
    CLIENT.connect()
    CLIENT.add_update_handler(handle_message)

    if not CLIENT.is_user_authorized():
        logger.info("Current session is not authenticated. Need code.")
        CURRENT_STATE = states.STATE_WAIT_CODE
        send_code()
    else:
        logger.info("Successfully connected")
        CURRENT_STATE = states.STATE_READY


if __name__ == "__main__":
    logger.info("Starting everything...")
    threading.Thread(target=start_server).start()
    threading.Thread(target=connect_client).start()
