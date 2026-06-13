import json

LOG_FILE = (
    "/home/user/xavier_nx_ai/crypto/trade_log.json"
)


def save_trade(
    ticker,
    buy_price,
    sell_price,
    reason
):

    profit = (
        sell_price
        /
        buy_price
        - 1
    ) * 100

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

    logs.append(

        {

            "ticker": ticker,

            "buy_price": buy_price,

            "sell_price": sell_price,

            "profit": round(
                profit,
                2
            ),

            "reason": reason

        }

    )

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            logs,
            f,
            ensure_ascii=False,
            indent=4
        )


if __name__ == "__main__":

    print(
        "trade_logger ready"
    )