import json

LOG_FILE = (
    "/home/user/xavier_nx_ai/crypto/trade_log.json"
)


def show_performance():

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            logs = json.load(
                f
            )

    except:

        logs = []

    if len(logs) == 0:

        print(
            "거래 기록 없음"
        )

        return

    total_trade = len(
        logs
    )

    win_count = 0

    total_profit = 0

    max_profit = -999

    max_loss = 999

    for trade in logs:

        profit = trade["profit"]

        total_profit += profit

        if profit > 0:

            win_count += 1

        if profit > max_profit:

            max_profit = profit

        if profit < max_loss:

            max_loss = profit

    win_rate = (
        win_count
        /
        total_trade
        * 100
    )

    avg_profit = (
        total_profit
        /
        total_trade
    )

    print()

    print(
        "===== 성과 분석 ====="
    )

    print(
        "총 거래 :",
        total_trade
    )

    print(
        "승률 :",
        round(
            win_rate,
            2
        ),
        "%"
    )

    print(
        "평균 수익률 :",
        round(
            avg_profit,
            2
        ),
        "%"
    )

    print(
        "누적 수익률 :",
        round(
            total_profit,
            2
        ),
        "%"
    )

    print(
        "최대 수익 :",
        round(
            max_profit,
            2
        ),
        "%"
    )

    print(
        "최대 손실 :",
        round(
            max_loss,
            2
        ),
        "%"
    )


if __name__ == "__main__":

    show_performance()