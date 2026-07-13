import json
import yfinance as yf

from llm.llm_client import ask_llm
from news.news_api import get_news
from news.news_api import get_news_sentiment


with open(
    "/home/user/xavier_nx_ai/stock/stocks.json",
    "r",
    encoding="utf-8"
) as f:
    STOCKS = json.load(f)


def find_stock(user_text):

    user_text = user_text.lower()

    for name in STOCKS:

        if name.lower() in user_text:
            return name, STOCKS[name]

    return None, None


def analyze_stock(user_text):

    stock_name, ticker = find_stock(user_text)

    if stock_name is None:
        return None

    df = yf.download(
        ticker,
        period="3mo",
        progress=False
    )

    if len(df) == 0:
        return "주가 데이터를 가져오지 못했습니다."

    current_price = int(df["Close"].iloc[-1].iloc[0])

    ma20 = int(df["Close"].rolling(20).mean().iloc[-1].iloc[0])
    ma60 = int(df["Close"].rolling(60).mean().iloc[-1].iloc[0])

    high_price = int(df["High"].max().iloc[0])

    # RSI 계산
    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    rsi = int(
        (
            100 -
            (
                100 /
                (
                    1 + rs
                )
            )
        ).iloc[-1].iloc[0]
    )

    if rsi >= 70:
        rsi_state = "과매수"

    elif rsi <= 30:
        rsi_state = "과매도"

    else:
        rsi_state = "중립"

    # 추세 판단
    if current_price > ma20 > ma60:
        trend = "상승"
        action = "매수"

    elif current_price > ma60:
        trend = "횡보"
        action = "보유"

    else:
        trend = "하락"
        action = "관망"

    news_sentiment = get_news_sentiment(stock_name)
    news_titles = get_news(stock_name)

    # 뉴스가 3개 미만이어도 안전하게 처리
    if len(news_titles) == 0:
        news_block = "• (최근 뉴스를 가져오지 못했습니다)\n"
    else:
        news_block = "".join(
            f"• {title}\n" for title in news_titles[:3]
        )

    buy_price = min(current_price, ma20)
    target_price = int(high_price * 0.95)
    stop_price = int(current_price * 0.93)

    prompt = f"""
    종목명 : {stock_name}

    차트 추세 : {trend}
    RSI 상태 : {rsi_state}
    뉴스 분위기 : {news_sentiment}

    정확히 두 문장만 출력하라.

    첫 번째 문장은 현재 상황 설명.
    두 번째 문장은 투자 의견.

    번호 금지.
    줄바꿈 금지.
    반드시 {action}, 보유, 관망 중 하나를 포함하라.
    """

    opinion = ask_llm(prompt)

    answer = (
        f"📈 {stock_name}\n\n"
        f"현재가 : {current_price:,}원\n"
        f"추천 매수가 : {buy_price:,}원\n"
        f"목표가 : {target_price:,}원\n"
        f"손절가 : {stop_price:,}원\n"
        f"RSI : {rsi} ({rsi_state})\n"
        f"뉴스 분위기 : {news_sentiment}\n\n"
        f"최근 뉴스\n"
        f"{news_block}\n"
        f"투자 의견 :\n"
        f"{opinion}"
    )

    return answer