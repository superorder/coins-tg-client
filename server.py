import requests
from os import environ

from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage

coins_secret = environ.get('COINS_SECRET', '')
ipn_url = environ.get('COINS_IPN_URL')


def update_handler(update):
    try:
        if (hasattr(update, 'message')):
            response = requests.post(
                ipn_url, data={'message': update.message, 'sign': '123'})
            if response.status_code != 200:
                print("Computer says: NO")

    except Exception as e:
        print(e)


if __name__ == '__main__':
    session_name = environ.get('TG_SESSION')
    user_phone = environ.get('TG_PHONE')
    client = TelegramClient(
        session_name, int(environ.get('TG_API_ID')
                          ), environ.get('TG_API_HASH'),
        proxy=None, update_workers=4
    )
    try:
        print('INFO: Connecting to Telegram Servers...', end='', flush=True)
        client.connect()
        print('Done!')

        if not client.is_user_authorized():
            print('INFO: Unauthorized user')
            client.send_code_request(user_phone)
            code_ok = False
            while not code_ok:
                code = input('Enter the auth code: ')
                try:
                    code_ok = client.sign_in(user_phone, code)
                except SessionPasswordNeededError:
                    password = getpass('Two step verification enabled. '
                                       'Please enter your password: ')
                    code_ok = client.sign_in(password=password)
        print('INFO: Client initialized successfully!')

        client.add_update_handler(update_handler)
        input('Press Enter to stop this!\n')
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
