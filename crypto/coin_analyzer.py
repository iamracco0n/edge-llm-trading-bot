import sys

sys.path.append(
    "/home/user/xavier_nx_ai"
)

from crypto.indicators import get_indicators


def analyze_coin(ticker):

    data = get_indicators(ticker)

    if data is None:
        return None

    current_price = data["current_price"]

    ma20 = data["ma20"]

    ma60 = data["ma60"]

    rsi = data["rsi"]

    volume_ratio = data["volume_ratio"]

    return_1h = data["return_1h"]

    bb_upper = data["bb_upper"]

    atr = data["atr"]

    macd = data["macd"]

    signal = data["signal"]

    current_4h = data["current_4h"]

    ma20_4h = data["ma20_4h"]

    score = 0

    # ==================
    # 추세
    # ==================
    if current_price > ma20 > ma60:

        trend = "상승"

        score += 40

    elif current_price > ma60:

        trend = "횡보"

        score += 20

    else:

        trend = "하락"

        score -= 30

    # ==================
    # RSI
    # ==================
    if 45 <= rsi <= 60:
    
        score += 30
    
    elif 35 <= rsi < 60:
    
        score += 20
    
    elif 25 <= rsi < 35:
    
        score += 10
    
    elif 60 <= rsi < 70:
    
        score += 0
    
    elif 70 <= rsi < 75:
    
        score -= 20
    
    else:
    
        score -= 100

    # ==================
    # 거래량
    # ==================
    if volume_ratio > 2:

        score += 20

    elif volume_ratio > 1:

        score += 10

    elif volume_ratio > 0.7:

        score += 5

    elif volume_ratio < 0.1:

        score -= 100

    elif volume_ratio < 0.2:

        score -= 20
        
    elif volume_ratio < 0.3:
    
        score -= 50

    elif volume_ratio < 0.5:

        score -= 20

    # ==================
    # 최근 1시간 상승률
    # ==================
    if return_1h > 5:

        score -= 20

    elif return_1h > 3:

        score -= 10

    elif 0 < return_1h < 2:

        score += 10

    # ==================
    # 볼린저
    # ==================
    if current_price > bb_upper:

        score -= 15

    # ==================
    # ATR
    # ==================
    atr_ratio = atr / current_price

    if atr_ratio > 0.03:

        score -= 15

    elif atr_ratio < 0.01:

        score += 5

    # ==================
    # MACD
    # ==================
    if macd > signal:

        score += 10

    else:

        score -= 10

    # ==================
    # 4시간봉 추세
    # ==================
    if current_4h > ma20_4h:

        score += 10

    else:

        score -= 30

    return {

        "ticker": ticker,

        "score": score,

        "trend": trend,

        "current_price": current_price,

        "rsi": round(rsi, 1),

        "volume_ratio": round(volume_ratio, 2),

        "return_1h": round(return_1h, 2),

        "atr_ratio": round(atr_ratio, 4)

    }


if __name__ == "__main__":

    print(
        analyze_coin(
            "KRW-BTC"
        )
    )