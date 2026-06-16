import json
import time
import sys

sys.path.append(
    "/home/user/xavier_nx_ai"
)

from crypto.upbit_api import get_current_price


POSITION_FILE = (
    "/home/user/xavier_nx_ai/crypto/position.json"
)


def load_positions():

    try:

        with open(
            POSITION_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = f.read()

            if data.strip() == "":

                return {}

            return json.loads(
                data
            )

    except:

        return {}


def get_portfolio_status():

    positions = load_positions()

    if len(
        positions
    ) == 0:

        return "보유 종목 없음"

    total_buy = 0

    total_current = 0

    message = "📊 현재 포트폴리오\n\n"

    count = 1

    for ticker in positions:

        buy_price = positions[ticker][
            "buy_price"
        ]

        buy_time = positions[ticker][
            "buy_time"
        ]

        quantity = positions[ticker].get(

            "quantity",

            50000 / buy_price

        )

        current_price = get_current_price(
            ticker
        )

        buy_total = (
            buy_price
            *
            quantity
        )

        current_total = (
            current_price
            *
            quantity
        )

        total_buy += buy_total

        total_current += current_total

        profit = (
            current_price
            /
            buy_price
            - 1
        ) * 100

        hold_hours = (
            time.time()
            -
            buy_time
        ) / 3600

        message += (

            f"{count}️⃣ {ticker}\n"

            f"매수가 : {buy_price:,.0f}원\n"

            f"매수수량 : {quantity:,.6f}개\n\n"

            f"매수총액 : {buy_total:,.0f}원\n"

            f"현재총액 : {current_total:,.0f}원\n\n"

            f"수익률 : {profit:.2f}%\n"

            f"보유시간 : {hold_hours:.1f}시간\n\n"

        )

        count += 1

    total_profit = (

        total_current
        /
        total_buy
        - 1

    ) * 100

    header = (

        "📊 현재 포트폴리오\n\n"

        f"💰 총 투자금 : {total_buy:,.0f}원\n"

        f"💵 현재 평가금 : {total_current:,.0f}원\n"

        f"📈 총 수익률 : {total_profit:.2f}%\n\n"

    )

    return header + message


if __name__ == "__main__":

    print(
        get_portfolio_status()
    )