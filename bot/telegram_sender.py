import asyncio

from telegram import Bot

from crypto.portfolio_manager import (
    get_portfolio_status
)


import json as _json
with open("/home/user/xavier_nx_ai/secrets/telegram.json") as _f: _tg = _json.load(_f)
TOKEN = _tg["token"]

CHAT_ID = _tg["chat_id"]


async def send_message(text):

    bot = Bot(
        token=TOKEN
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )


def notify(text):

    try:

        asyncio.run(
            send_message(
                text
            )
        )

    except:

        pass


if __name__ == "__main__":

    notify(
        "텔레그램 알림 테스트"
    )