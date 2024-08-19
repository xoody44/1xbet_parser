import requests

from config import TG_CHAT, TGBOT_TOKEN


def send_message(text: str):
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
    if r.status_code != 200:
        raise Exception("post_text error")


def main():
    send_message("44")


if __name__ == "__main__":
    main()