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
from market.recommend_stock import get_recommend_stocks
from daily_market_report import create_report

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
            "🟢 Xavier NX AI 정상 동작중\n"
            "LLM : Qwen2.5-1.5B\n"
            "Server : localhost:8080"
        )

        return

    # 시장 브리핑
    if (
        user_text == "/brief"
        or
        user_text == "오늘 브리핑"
    ):

        await update.message.reply_text(
            "📊 시장 브리핑 생성중..."
        )

        answer = create_report()

        await update.message.reply_text(answer)

        return


    # 추천 종목
    if user_text == "/추천":

        stocks = get_recommend_stocks()

        if len(stocks) == 0:

            await update.message.reply_text(
                "추천 종목을 찾지 못했습니다."
            )

            return

        top_trend = stocks[0]["trend"]

        if top_trend == "상승":

            opinion = (
                "상위 추천 종목들이 상승 추세를 유지하고 있습니다.\n"
                "분할 매수 관점에서 접근하는 것이 유리해 보입니다."
            )

        elif top_trend == "횡보":

            opinion = (
                "시장 전체가 횡보 구간에 위치하고 있습니다.\n"
                "보수적인 접근과 분할 매수를 고려할 수 있습니다."
            )

        else:

            opinion = (
                "시장 변동성이 커지고 있습니다.\n"
                "관망 또는 비중 축소를 고려하는 것이 좋습니다."
            )

        answer = (
            "📈 AI 추천 종목\n\n"

            f"1. {stocks[0]['name']}\n"
            f"매수 : {stocks[0]['buy_price']:,}원\n"
            f"목표 : {stocks[0]['target_price']:,}원\n"
            f"손절 : {stocks[0]['stop_price']:,}원\n\n"

            f"2. {stocks[1]['name']}\n"
            f"매수 : {stocks[1]['buy_price']:,}원\n"
            f"목표 : {stocks[1]['target_price']:,}원\n"
            f"손절 : {stocks[1]['stop_price']:,}원\n\n"

            f"3. {stocks[2]['name']}\n"
            f"매수 : {stocks[2]['buy_price']:,}원\n"
            f"목표 : {stocks[2]['target_price']:,}원\n"
            f"손절 : {stocks[2]['stop_price']:,}원\n\n"

            "📝 AI 의견\n"
            f"{opinion}"
        )

        print("답변 :", answer)

        await update.message.reply_text(answer)

        return


    # 개별 종목 분석
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