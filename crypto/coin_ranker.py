import json
import sys

sys.path.append(
    "/home/user/xavier_nx_ai"
)

from crypto.coin_analyzer import analyze_coin


with open(
    "/home/user/xavier_nx_ai/crypto/coins.json",
    "r",
    encoding="utf-8"
) as f:

    COINS = json.load(f)


def get_top_coins():

    results = []

    for ticker in COINS:

        try:

            data = analyze_coin(
                ticker
            )

            if data is not None:

                results.append(
                    data
                )

        except Exception as e:

            print(
                ticker,
                e
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:10]


if __name__ == "__main__":

    top10 = get_top_coins()

    print()

    print(
        "===== TOP10 ====="
    )

    for i, coin in enumerate(top10):

        print(
            f"{i+1}. "
            f"{coin['ticker']}  "
            f"{coin['score']}점  "
            f"{coin['trend']}  "
            f"RSI:{coin['rsi']}  "
            f"VOL:{coin['volume_ratio']}  "
            f"1H:{coin['return_1h']}%"
        )