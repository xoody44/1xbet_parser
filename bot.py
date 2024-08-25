import requests

from loguru import logger

from config import TG_CHAT, TGBOT_TOKEN


def send_message(text: str):
    try:
        token = TGBOT_TOKEN
        url = "https://api.telegram.org/bot"
        chat_id = TG_CHAT
        url += token
        method = url + "/sendMessage"

        r = requests.post(method, data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
    except Exception as ex:
        logger.error(f"error with connection: {ex}")


def main():
    send_message("test")


if __name__ == "__main__":
    main()
