import pyupbit


def get_indicators(ticker):

    df = pyupbit.get_ohlcv(
        ticker,
        interval="minute5",
        count=100
    )

    if df is None:
        return None

    # ==================
    # 4시간봉 데이터
    # ==================
    df4h = pyupbit.get_ohlcv(
        ticker,
        interval="minute240",
        count=60
    )
    
    if df4h is None:
        return None

    current_price = float(
        df["close"].iloc[-1]
    )

    # ==================
    # 이동평균
    # ==================
    ma20 = float(
        df["close"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    ma60 = float(
        df["close"]
        .rolling(60)
        .mean()
        .iloc[-1]
    )

    # ==================
    # RSI(14)
    # ==================
    delta = df["close"].diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    rsi = float(
        (
            100
            -
            (
                100
                /
                (
                    1 + rs
                )
            )
        ).iloc[-1]
    )

    # ==================
    # 거래량 비율
    # ==================
    volume_now = float(
        df["volume"].iloc[-1]
    )

    volume_avg20 = float(
        df["volume"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    volume_ratio = (
        volume_now
        /
        volume_avg20
    )

    # ==================
    # 최근 1시간 수익률
    # ==================
    return_1h = (
        current_price
        /
        float(
            df["close"].iloc[-13]
        )
        - 1
    ) * 100

    # ==================
    # 4시간봉 추세
    # ==================
    current_4h = float(
        df4h["close"].iloc[-1]
    )

    ma20_4h = float(
        df4h["close"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    # ==================
    # 볼린저 밴드
    # ==================
    bb_mid = (
        df["close"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    bb_std = (
        df["close"]
        .rolling(20)
        .std()
        .iloc[-1]
    )

    bb_upper = (
        bb_mid
        +
        2 * bb_std
    )

    bb_lower = (
        bb_mid
        -
        2 * bb_std
    )

    # ==================
    # ATR(14)
    # ==================
    high_low = (
        df["high"]
        -
        df["low"]
    )

    high_close = (
        df["high"]
        -
        df["close"].shift()
    ).abs()

    low_close = (
        df["low"]
        -
        df["close"].shift()
    ).abs()

    tr = (
        high_low
        .combine(high_close, max)
        .combine(low_close, max)
    )

    atr = float(
        tr
        .rolling(14)
        .mean()
        .iloc[-1]
    )

    # ==================
    # MACD
    # ==================
    ema12 = (
        df["close"]
        .ewm(span=12)
        .mean()
    )

    ema26 = (
        df["close"]
        .ewm(span=26)
        .mean()
    )

    macd = float(
        (
            ema12
            -
            ema26
        ).iloc[-1]
    )

    signal = float(
        (
            (
                ema12
                -
                ema26
            )
            .ewm(span=9)
            .mean()
        ).iloc[-1]
    )

    return {

        "current_price": current_price,

        "ma20": ma20,

        "ma60": ma60,

        "rsi": rsi,

        "volume_ratio": volume_ratio,

        "return_1h": return_1h,

        "bb_upper": bb_upper,

        "bb_lower": bb_lower,

        "atr": atr,

        "macd": macd,

        "signal": signal,

        "current_4h": current_4h,
        
        "ma20_4h": ma20_4h

    }


if __name__ == "__main__":

    print(
        get_indicators(
            "KRW-BTC"
        )
    )