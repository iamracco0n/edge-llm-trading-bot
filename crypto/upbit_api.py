import json
import pyupbit


with open(
    "/home/user/xavier_nx_ai/secrets/upbit_key.json",
    "r",
    encoding="utf-8"
) as f:

    KEY = json.load(f)


ACCESS_KEY = KEY["access_key"]
SECRET_KEY = KEY["secret_key"]

upbit = pyupbit.Upbit(
    ACCESS_KEY,
    SECRET_KEY
)


def get_krw_balance():

    return upbit.get_balance(
        "KRW"
    )


def get_coin_balance(ticker):

    currency = ticker.replace(
        "KRW-",
        ""
    )

    return upbit.get_balance(
        currency
    )


def get_current_price(ticker):

    return pyupbit.get_current_price(
        ticker
    )

def buy_coin(
    ticker,
    amount
):

    print(
        "[가상매수]",
        ticker,
        amount
    )

    # =========================
    # 실거래 코드
    # =========================
    #
    # result = upbit.buy_market_order(
    #     ticker,
    #     amount
    # )
    #
    # print(
    #     result
    # )
    #
    # return result

    return {

        "result": "success"

    }


def sell_coin(
    ticker,
    quantity=None
):

    currency = ticker.replace(
        "KRW-",
        ""
    )

    # 매도 수량 결정:
    # - quantity 가 주어지면 해당 포지션 수량만 매도
    # - 없으면 지갑 잔고 전량 (하위호환)
    if quantity is None:

        quantity = upbit.get_balance(
            currency
        )

    # =========================
    # 가상매도
    # =========================
    print(
        "[가상매도]",
        ticker,
        quantity
    )

    return {

        "result": "success"

    }

    # =========================
    # 실거래 코드
    # =========================
    #
    # if quantity is None or float(quantity) == 0:
    #
    #     return None
    #
    # print(
    #     "매도 :",
    #     ticker,
    #     quantity
    # )
    #
    # return upbit.sell_market_order(
    #     ticker,
    #     quantity
    # )

def get_my_coins():

    balances = upbit.get_balances()

    coins = []

    for balance in balances:

        currency = balance["currency"]

        if currency != "KRW":

            coins.append(
                {
                    "ticker": "KRW-" + currency,
                    "balance": float(
                        balance["balance"]
                    )
                }
            )

    return coins


if __name__ == "__main__":

    print(
        get_my_coins()
    )