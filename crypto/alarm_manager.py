import time

from bot.telegram_sender import notify


def buy_alarm(
    ticker,
    score,
    current_price,
    amount
):

    quantity = round(
        amount / current_price,
        6
    )

    print(
        "\n=================================="
    )

    print(
        "🟢 신규 매수"
    )

    print(
        "종목 :",
        ticker
    )

    print(
        "점수 :",
        score
    )

    print(
        "현재가 :",
        f"{current_price:,.0f} 원"
    )

    print(
        "매수금액 :",
        f"{amount:,} 원"
    )

    print(
        "수량 :",
        quantity
    )

    print(
        "=================================="
    )

    notify(

        f"🟢 신규 매수\n\n"

        f"종목 : {ticker}\n"

        f"점수 : {score}\n"

        f"현재가 : {current_price:,.0f}원\n"

        f"매수금액 : {amount:,}원\n"

        f"수량 : {quantity}\n"

        f"시간 : {time.strftime('%m-%d %H:%M')}"

    )


def sell_alarm(
    ticker,
    buy_price,
    current_price,
    profit,
    hold_hours,
    reason
):

    print(
        "\n=================================="
    )

    print(
        reason
    )

    print(
        "종목 :",
        ticker
    )

    print(
        "매수가 :",
        f"{buy_price:,.0f} 원"
    )

    print(
        "현재가 :",
        f"{current_price:,.0f} 원"
    )

    print(
        "수익률 :",
        round(
            profit * 100,
            2
        ),
        "%"
    )

    print(
        "보유시간 :",
        round(
            hold_hours,
            1
        ),
        "시간"
    )

    print(
        "=================================="
    )

    notify(

        f"{reason}\n\n"

        f"종목 : {ticker}\n"

        f"매수가 : {buy_price:,.0f}원\n"

        f"현재가 : {current_price:,.0f}원\n"

        f"수익률 : {round(profit*100,2)}%\n"

        f"보유시간 : {round(hold_hours,1)}시간"

    )