import json
import sys
import time

sys.path.append(
    "/home/user/xavier_nx_ai"
)

from crypto.coin_ranker import get_top_coins
from crypto.trade_logger import save_trade
from crypto.coin_analyzer import analyze_coin
from bot.telegram_sender import notify

from crypto.alarm_manager import (
    buy_alarm,
    sell_alarm
)

from crypto.upbit_api import (
    buy_coin,
    sell_coin,
    get_current_price
)

POSITION_FILE = (
    "/home/user/xavier_nx_ai/crypto/position.json"
)

BUY_AMOUNT = 50000

MAX_POSITION = 3

TAKE_PROFIT = 0.03

STOP_LOSS = -0.04

MAX_HOLD_HOURS = 72


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


def save_positions(position):

    with open(
        POSITION_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            position,
            f,
            ensure_ascii=False,
            indent=4
        )


def manage_trade():

    positions = load_positions()

    remove_list = []

    # ==========================
    # 보유 종목 관리
    # ==========================
    for ticker in positions:

        buy_price = positions[ticker]["buy_price"]

        buy_time = positions[ticker]["buy_time"]

        quantity = positions[ticker].get("quantity")

        current_price = get_current_price(
            ticker
        )

        profit = (
            current_price
            /
            buy_price
            - 1
        )

        hold_hours = (
            time.time()
            -
            buy_time
        ) / 3600

        print(
            ticker,
            round(
                profit * 100,
                2
            ),
            "%",
            round(
                hold_hours,
                1
            ),
            "시간"
        )

        # ===================
        # 익절
        # ===================
        if profit >= TAKE_PROFIT:

            sell_coin(
                ticker,
                quantity
            )
            
            save_trade(
            
                ticker,
            
                buy_price,
            
                current_price,
            
                "익절"
            
            )
            
            sell_alarm(
            
                ticker,
            
                buy_price,
            
                current_price,
            
                profit,
            
                hold_hours,
            
                "🔴 익절"
            
            )
            
            remove_list.append(
                ticker
            )
            
            continue

        # ===================
        # 손절
        # ===================
        if profit <= STOP_LOSS:

            sell_coin(
                ticker,
                quantity
            )
            
            save_trade(
            
                ticker,
            
                buy_price,
            
                current_price,
            
                "손절"
            
            )

            sell_alarm(
            
                ticker,
            
                buy_price,
            
                current_price,
            
                profit,
            
                hold_hours,
            
                "🔵 손절"
            
            )
            
            remove_list.append(
                ticker
            )

            continue

        # ===================
        # 최대 보유시간
        # ===================
        if hold_hours >= MAX_HOLD_HOURS:
        
            if profit > 0.0025:

                sell_coin(
                    ticker,
                    quantity
                )
        
                save_trade(
        
                    ticker,
        
                    buy_price,
        
                    current_price,
        
                    "시간만료"
        
                )
        
                sell_alarm(
                
                    ticker,
                
                    buy_price,
                
                    current_price,
                
                    profit,
                
                    hold_hours,
                
                    "⏰ 시간만료"
                
                )
        
                remove_list.append(
                    ticker
                )
        
                continue
        
            else:
        
                print(
        
                    ticker,
        
                    "보유기간 연장"
        
                )
        
                positions[ticker][
                    "buy_time"
                ] = time.time()

                save_positions(
                    positions
                )
        

        
        # ===================
        # 추세 붕괴
        # ===================
        data = analyze_coin(
            ticker
        )

        if data is not None:

            if data["trend"] == "하락":

                positions[ticker][
                    "trend_break_count"
                ] += 1

                count = positions[ticker][
                    "trend_break_count"
                ]

                print(

                    ticker,

                    "하락",

                    count,

                    "/5"

                )

                if count >= 5:

                    sell_coin(
                        ticker,
                        quantity
                    )

                    save_trade(

                        ticker,

                        buy_price,

                        current_price,

                        "추세붕괴"

                    )

                    sell_alarm(

                        ticker,

                        buy_price,

                        current_price,

                        profit,

                        hold_hours,

                        "⚠️ 추세붕괴"

                    )

                    remove_list.append(
                        ticker
                    )

                    continue

            else:

                positions[ticker][
                    "trend_break_count"
                ] = 0

                
    # ==========================
    # 제거
    # ==========================
    for ticker in remove_list:

        del positions[ticker]

    save_positions(
        positions
    )

    # ==========================
    # 신규 매수
    # ==========================
    holding_list = list(
        positions.keys()
    )

    # ==========================
    # BTC 추세 확인
    # ==========================
    btc_data = analyze_coin(
        "KRW-BTC"
    )
    
#    if btc_data is not None:
    #
#        if btc_data["score"] < -50:
#                
#
#            print(
#                "BTC 약세 → 신규 매수 중단"
#            )
#
#            save_positions(
#                positions
#            )
#
#            return

    top_coins = get_top_coins()

    for coin in top_coins:

        print(
            coin
        )
        
        ticker = coin["ticker"]

        score = coin["score"]

        if len(
            holding_list
        ) >= MAX_POSITION:

            break

        if ticker in positions:

            continue

        if score < 80:

            print(
                ticker,
                score,
                "점수 부족"
            )
            continue

        data = analyze_coin(
            ticker
        )

        if data is None:

            continue

        if data["volume_ratio"] < 0.8:

            print(

                ticker,

                "거래량 부족"

            )

            continue

        if data["rsi"] > 70:

            print(

                ticker,

                "RSI 과열"

            )

            continue

        current_price = coin[
            "current_price"
        ]


        quantity = round(
            BUY_AMOUNT / current_price,
            6
        )

        # 실제 매수 주문 (가상매매 모드에서는 시뮬레이션)
        buy_coin(
            ticker,
            BUY_AMOUNT
        )

        buy_alarm(

            ticker,

            score,

            current_price,

            BUY_AMOUNT

        )


        positions[ticker] = {
        
            "buy_price":
            current_price,
        
            "buy_time":
            time.time(),
        
            "quantity":
            quantity,
        
            "trend_break_count":
            0
        
        }

        holding_list.append(
            ticker
        )
        

    save_positions(
        positions
    )


if __name__ == "__main__":

    manage_trade()