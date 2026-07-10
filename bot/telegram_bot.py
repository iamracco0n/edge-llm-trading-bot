import sys
sys.path.append("/home/user/xavier_nx_ai")

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

from llm.llm_client import ask_llm
from stock.stock_analyzer import analyze_stock
from daily_market_report import create_report

################################################
from crypto.portfolio_manager import (
    get_portfolio_status
)


import json as _json
with open("/home/user/xavier_nx_ai/secrets/telegram.json") as _f: _tg = _json.load(_f)
TOKEN = _tg["token"]


async def reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_text = update.message.text

    print("질문 :", user_text)

    # 상태 확인
    if user_text == "/status":

        await update.message.reply_text(
            f"🟢 Xavier NX AI 정상 동작중\n"
            f"LLM : Qwen2.5-1.5B\n"
            f"Server : localhost:8080\n"
            f"CHAT_ID : {update.message.chat_id}"
        )

        return

######
    if user_text == "/coin":

        answer = get_portfolio_status()

        await update.message.reply_text(
            answer
        )

        return
######

    # 아침 브리핑
    if (
        user_text == "오늘 브리핑"
        or
        user_text == "/brief"
    ):

        await update.message.reply_text(
            "📊 시장 브리핑 생성중..."
        )

        answer = create_report()

        await update.message.reply_text(answer)

        return

    # 주식 분석
    answer = analyze_stock(user_text)

    if answer is not None:

        print("답변 :", answer)

        await update.message.reply_text(answer)

        return

    # 일반 대화
    answer = ask_llm(user_text)

    print("답변 :", answer)

    await update.message.reply_text(answer)


app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)

app.add_handler(
    MessageHandler(
        filters.TEXT,
        reply
    )
)

print("Telegram AI Bot Start")

app.run_polling()