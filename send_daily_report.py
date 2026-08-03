import sys
sys.path.append("/home/user/xavier_nx_ai")

import time
import asyncio
import urllib.request
from telegram import Bot

from daily_market_report import create_report


import json as _json
with open("/home/user/xavier_nx_ai/secrets/telegram.json") as _f: _tg = _json.load(_f)
TOKEN = _tg["token"]
CHAT_ID = _tg["chat_id"]

HEALTH_URL = "http://127.0.0.1:8080/health"


def wait_for_llm(max_wait=720, interval=20):
    """llama-server가 응답할 때까지 대기. 08:00 크론이 llama 재시작 구간과 겹치면
    LLM 호출이 전부 실패해 '심층분석 없는 반쪽 브리핑'이 조용히 나간다(2026-08-03 실제 발생).
    준비될 때까지 기다린 뒤 리포트를 만들고, 끝내 안 뜨면 그 사실을 브리핑에 명시한다."""
    deadline = time.time() + max_wait
    while True:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=5) as r:
                if r.getcode() == 200:
                    return True
        except Exception:
            pass
        if time.time() >= deadline:
            return False
        print(f"[wait] LLM 서버 대기중... ({int(deadline - time.time())}초 남음)", flush=True)
        time.sleep(interval)


async def send_report():

    bot = Bot(token=TOKEN)

    llm_ok = wait_for_llm()
    if not llm_ok:
        print("[warn] LLM 서버 끝내 미응답 — 심층분석 없이 진행")

    message = create_report()

    if not llm_ok:
        message = ("⚠️ LLM 서버 미응답 — 아래 브리핑은 심층분석 없이 생성됨\n\n" + message)

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
