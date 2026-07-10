import sys
sys.path.append("/home/user/xavier_nx_ai")

import asyncio
from telegram import Bot

from daily_market_report import create_report


import json as _json
with open("/home/user/xavier_nx_ai/secrets/telegram.json") as _f: _tg = _json.load(_f)
TOKEN = _tg["token"]
CHAT_ID = _tg["chat_id"]


async def send_report():

    bot = Bot(token=TOKEN)

    message = create_report()

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

    print("브리핑 전송 완료")


asyncio.run(
    send_report()
)