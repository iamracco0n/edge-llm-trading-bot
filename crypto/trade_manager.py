# -*- coding: utf-8 -*-
"""국면 적응형 코인 자동매매 (현물/업비트).

시장 국면(상승/하락/횡보)을 판단해 국면별 전략을 갈아탄다:
  상승장 → 추세추종 롱 (눌림목 매수, +3% 익절 / 국면전환·손절 청산)
  횡보장 → 평균회귀 롱 (볼린저 하단 과매도 매수, 평균MA20 복귀·과열 매도)
  하락장 → 현금 방어 (신규 매수 중단)

전략 원리는 백테스트 저장소 iamracco0n/llm-trading-backtest 의
regime_adaptive(v4)에서 이식. 그 v4는 하락장에 '숏'으로 수익을 내지만
업비트는 현물 전용이라 여기서는 하락장에 현금 보유(방어)로 대체한다.
(90일 다국면 백테스트에서 v4가 단일 전략을 압도: +4.36% vs 추세추종 +1.39%)

텔레그램 알림·주문·포지션 저장은 기존 그대로 유지.
"""
import json
import time

from crypto.indicators import get_indicators
from crypto.trade_logger import save_trade
from crypto.alarm_manager import buy_alarm, sell_alarm
from crypto.upbit_api import buy_coin, sell_coin

POSITION_FILE = "/home/user/xavier_nx_ai/crypto/position.json"
COINS_FILE = "/home/user/xavier_nx_ai/crypto/coins.json"

# ===== 공통 매매 조건 =====
BUY_AMOUNT = 50000
MAX_POSITION = 3
TAKE_PROFIT = 0.03      # +3% 익절 (추세)
STOP_LOSS = -0.04       # -4% 손절 (공통)
MAX_HOLD_HOURS = 72

# ===== 국면 판단 (MA20-MA60 이격도로 추세 강도 게이팅) =====
TREND_SEP = 0.006       # 이격 0.6% 이상이어야 '강한 추세', 아니면 횡보 취급

# ===== 평균회귀 (횡보장) =====
MR_RSI_BUY = 35         # 이하 과매도 → 매수
MR_RSI_SELL = 65        # 이상 과열 → 매도
KNIFE_1H = -6.0         # 최근 1시간 이보다 급락이면 낙하칼 → 매수 회피


def load_positions():
    try:
        with open(POSITION_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else {}
    except Exception:
        return {}


def save_positions(positions):
    with open(POSITION_FILE, "w", encoding="utf-8") as f:
        json.dump(positions, f, ensure_ascii=False, indent=4)


def load_coins():
    with open(COINS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_regime(ind):
    """지표로 국면 판단: up / down / range.
    강한 추세(MA 이격 + 4시간봉 방향 일치)일 때만 up/down, 아니면 range."""
    up_4h = ind["current_4h"] > ind["ma20_4h"]
    price, ma20, ma60 = ind["current_price"], ind["ma20"], ind["ma60"]
    sep = (ma20 - ma60) / ma60 if ma60 else 0
    if price > ma20 and sep > TREND_SEP and up_4h:
        return "up"
    if price < ma20 and sep < -TREND_SEP and not up_4h:
        return "down"
    return "range"


def manage_trade():
    positions = load_positions()
    remove_list = []

    # ==========================
    # 보유 종목 관리 (청산)
    # ==========================
    for ticker in list(positions.keys()):
        ind = get_indicators(ticker)
        if ind is None:
            continue
        pos = positions[ticker]
        price = ind["current_price"]
        buy_price = pos["buy_price"]
        quantity = pos.get("quantity")
        profit = price / buy_price - 1
        hold_hours = (time.time() - pos["buy_time"]) / 3600
        strat = pos.get("strat", "trend")
        regime = classify_regime(ind)

        label = None
        if profit <= STOP_LOSS:
            label = "🔵 손절"
        elif hold_hours >= MAX_HOLD_HOURS:
            label = "⏰ 시간만료"
        elif strat == "trend":
            if profit >= TAKE_PROFIT:
                label = "🔴 익절"
            elif regime == "down":                 # 상승장서 샀는데 하락 전환
                label = "⚠️ 국면전환"
        else:  # 평균회귀 포지션
            if price >= ind["ma20"] or price >= ind["bb_upper"] or ind["rsi"] >= MR_RSI_SELL:
                label = "🟣 평균복귀익절"

        if label:
            sell_coin(ticker, quantity)
            save_trade(ticker, buy_price, price, label)
            sell_alarm(ticker, buy_price, price, profit, hold_hours, label)
            remove_list.append(ticker)

    for ticker in remove_list:
        del positions[ticker]
    save_positions(positions)

    # ==========================
    # 신규 진입 (국면별)
    # ==========================
    candidates = []  # (우선순위, 정렬키, ticker, price, strat, 사유)
    for ticker in load_coins():
        if ticker in positions:
            continue
        ind = get_indicators(ticker)
        if ind is None:
            continue
        regime = classify_regime(ind)
        if regime == "up":
            # 상승장 → 추세추종: 과열아님 + MACD 상향 + 거래량
            if ind["rsi"] <= 70 and ind["macd"] > ind["signal"] and ind["volume_ratio"] >= 0.8:
                candidates.append((0, -ind["macd"], ticker, ind["current_price"],
                                   "trend", "상승추세"))
        elif regime == "range":
            # 횡보장 → 평균회귀: 볼린저 하단 + 과매도 + 낙하칼 아님
            if ind["current_price"] <= ind["bb_lower"] and ind["rsi"] <= MR_RSI_BUY \
               and ind["return_1h"] > KNIFE_1H:
                candidates.append((1, ind["rsi"], ticker, ind["current_price"],
                                   "meanrev", f"과매도RSI{ind['rsi']:.0f}"))
        # down → 현금 방어(신규매수 안 함)

    candidates.sort(key=lambda x: (x[0], x[1]))
    for _, _, ticker, price, strat, reason in candidates:
        if len(positions) >= MAX_POSITION:
            break
        buy_coin(ticker, BUY_AMOUNT)
        buy_alarm(ticker, reason, price, BUY_AMOUNT)
        positions[ticker] = {
            "buy_price": price,
            "buy_time": time.time(),
            "quantity": round(BUY_AMOUNT / price, 6),
            "strat": strat,
            "trend_break": 0,
        }

    save_positions(positions)


if __name__ == "__main__":
    manage_trade()
