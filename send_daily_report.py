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

    # 텔레그램 4096자 제한 → 줄 단위로 청크 분할 (긴 심층분석 대비)
    MAX = 4000
    chunks = []
    while len(message) > MAX:
        cut = message.rfind("\n", 0, MAX)
        if cut <= 0:
            cut = MAX
        chunks.append(message[:cut])
        message = message[cut:]
    chunks.append(message)

    for ch in chunks:
        if ch.strip():
            await bot.send_message(
                chat_id=CHAT_ID,
                text=ch
            )

    print(f"브리핑 전송 완료 ({len(chunks)}개 메시지)")


asyncio.run(
    send_report()
)