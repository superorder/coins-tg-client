from os import environ
from flask import Flask, request, render_template, redirect
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from requests import post
import time
import logging

import states
import crypto_utils

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


@APP.route('/', methods=['GET'])
def index():
    global CURRENT_STATE

    templates = {
        states.STATE_WAIT_CODE: 'wait_code.html',
        states.STATE_WAIT_PASSWORD: 'wait_password.html',
        states.STATE_READY: 'ready.html',
    }

    if CURRENT_STATE in templates:
        return render_template(templates[CURRENT_STATE])

    return render_template('init.html')


@APP.route('/', methods=['POST'])
def index_post():
    global CURRENT_STATE, CLIENT

    if CURRENT_STATE == states.STATE_WAIT_CODE:
        form = request.form
        try:
            if CLIENT.sign_in(phone=PHONE, code=form['code']):
                CURRENT_STATE = states.STATE_READY
        except SessionPasswordNeededError:
            CURRENT_STATE = states.STATE_WAIT_PASSWORD

    if CURRENT_STATE == states.STATE_WAIT_PASSWORD:
        form = request.form
        if CLIENT.sign_in(password=form['password']):
            CURRENT_STATE = states.STATE_READY

    return redirect('/')


def update_handler(update):
    try:
        if hasattr(update, 'message'):
            print(update)
            data = {'message': update.message}
            hmac = crypto_utils.sign(IPN_SECRET, data)
            response = post(IPN_URL, data=data, headers={"hmac": hmac})
            if response.status_code != 200:
                print("Computer says: NO")
    except Exception as exception:
        print(exception)

def send_code(client):
    try:
        client.send_code_request(phone=PHONE)
    except FloodWaitError as exception:
        logging.error(
            'Flood error occured. Waiting %d seconds...', exception.seconds)
        time.sleep(exception.seconds)
        send_code(client)

if __name__ == "__main__":
    logging.info("Connecting telegram client...")
    CLIENT.connect()
    CLIENT.add_update_handler(update_handler)

    if not CLIENT.is_user_authorized():
        logging.info('Current session is not authenticated. Need code.')
        send_code(CLIENT)
        CURRENT_STATE = states.STATE_WAIT_CODE
    else:
        logging.info('Successfully connected')
        CURRENT_STATE = states.STATE_READY

    logging.info('Staring web server...')
    APP.run()
