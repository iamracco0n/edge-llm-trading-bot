import json
import yfinance as yf

from news.news_api import get_news_sentiment


with open(
    "/home/user/xavier_nx_ai/stock/stocks.json",
    "r",
    encoding="utf-8"
) as f:
    STOCKS = json.load(f)


def get_recommend_stocks():

    candidates = []

    for stock_name, ticker in STOCKS.items():

        if ".KS" not in ticker and ".KQ" not in ticker:
            continue

        try:

            df = yf.download(
                ticker,
                period="3mo",
                progress=False
            )

            if len(df) < 60:
                continue

            current_price = float(
                df["Close"].iloc[-1].iloc[0]
            )

            ma20 = float(
                df["Close"].rolling(20).mean().iloc[-1].iloc[0]
            )

            ma60 = float(
                df["Close"].rolling(60).mean().iloc[-1].iloc[0]
            )

            delta = df["Close"].diff()

            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            rsi = float(
                (
                    100 - (100 / (1 + rs))
                ).iloc[-1].iloc[0]
            )

            volume_today = float(
                df["Volume"].iloc[-1].iloc[0]
            )

            volume_avg20 = float(
                df["Volume"].rolling(20).mean().iloc[-1].iloc[0]
            )

            volume_ratio = volume_today / volume_avg20

            score = 0

            # 추세
            if current_price > ma20 > ma60:
                score += 40
                trend = "상승"

            elif current_price > ma60:
                score += 20
                trend = "횡보"

            else:
                trend = "하락"

            # RSI
            if 40 <= rsi <= 65:
                score += 20

            elif 30 <= rsi <= 70:
                score += 10

            # 거래량
            if volume_ratio > 1:
                score += 20

            candidates.append(
                {
                    "name": stock_name,
                    "score": score,
                    "current_price": int(current_price),
                    "trend": trend,
                    "rsi": rsi,
                    "volume_ratio": volume_ratio
                }
            )

        except:
            continue

    # 1차 정렬
    candidates.sort(
        key=lambda x: (
            x["score"],
            x["volume_ratio"]
        ),
        reverse=True
    )

    # 상위 20개만 뉴스 점수 추가
    top20 = candidates[:20]

    for stock in top20:

        sentiment = get_news_sentiment(
            stock["name"]
        )

        if sentiment == "긍정":
            stock["score"] += 20

        elif sentiment == "중립":
            stock["score"] += 10

        stock["sentiment"] = sentiment

        current_price = stock["current_price"]

        if stock["trend"] == "상승":
            target_price = int(current_price * 1.12)

        elif stock["trend"] == "횡보":
            target_price = int(current_price * 1.08)

        else:
            target_price = int(current_price * 1.05)

        rsi = stock["rsi"]

        if rsi >= 70:
            stop_price = int(current_price * 0.95)

        elif rsi <= 30:
            stop_price = int(current_price * 0.90)

        else:
            stop_price = int(current_price * 0.93)

        stock["buy_price"] = current_price
        stock["target_price"] = target_price
        stock["stop_price"] = stop_price

    top20.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return top20[:3]