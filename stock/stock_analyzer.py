import json
import yfinance as yf

from llm.llm_client import deep_analyze
from news.news_api import get_news
from news.news_api import get_news_sentiment_llm
from market.recommend_stock_llm import chart_features


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

    # 뉴스는 한 번만 가져와 재사용 (API 중복 호출 제거)
    news_titles = get_news(stock_name)

    # 감성은 로컬 LLM이 제목을 직접 읽고 판정 (단어 카운팅 폐기)
    news_sentiment = get_news_sentiment_llm(news_titles)

    # 뉴스가 3개 미만이어도 안전하게 처리
    if len(news_titles) == 0:
        news_block = "• (최근 뉴스를 가져오지 못했습니다)\n"
    else:
        news_block = "".join(
            f"• {title}\n" for title in news_titles[:3]
        )

    buy_price = min(current_price, ma20)
    # 목표가는 항상 현재가보다 위에 오도록 (고점 근처 버그 수정)
    target_price = max(
        int(high_price * 0.98),
        int(current_price * 1.05)
    )
    stop_price = int(current_price * 0.93)

    # ===== LLM 심층 분석: 지표·뉴스를 통째로 먹여서 추론시킴 =====
    data_lines = [
        f"현재가 : {current_price:,}원",
        f"20일 이동평균(MA20) : {ma20:,}원",
        f"60일 이동평균(MA60) : {ma60:,}원",
        f"3개월 최고가 : {high_price:,}원",
        f"RSI(14) : {rsi} ({rsi_state})",
        f"차트 추세 : {trend}",
        *chart_features(df),
        f"뉴스 분위기(LLM 판정) : {news_sentiment}",
        f"규칙기반 참고가 → 매수 {buy_price:,} / 목표 {target_price:,} / 손절 {stop_price:,}",
        "최근 뉴스 제목 :",
    ]

    if len(news_titles) == 0:
        data_lines.append("  - (뉴스 없음)")
    else:
        for t in news_titles[:5]:
            data_lines.append(f"  - {t}")

    opinion = deep_analyze(
        title=stock_name,
        data_lines=data_lines,
        question=(
            f"지금 이 종목을 매수하는 게 타당한지 분석해줘. "
            f"추세({trend})와 RSI({rsi_state}), 뉴스({news_sentiment})가 "
            f"서로 부합하는지, 이동평균 배열과 최고가 대비 위치도 함께 고려해서 "
            f"결론은 {action}/보유/관망 중 하나로 내줘."
        )
    )

    answer = (
        f"📈 {stock_name}\n\n"
        f"현재가 : {current_price:,}원\n"
        f"추천 매수가 : {buy_price:,}원\n"
        f"목표가 : {target_price:,}원\n"
        f"손절가 : {stop_price:,}원\n"
        f"RSI : {rsi} ({rsi_state})\n"
        f"뉴스 분위기(AI) : {news_sentiment}\n\n"
        f"최근 뉴스\n"
        f"{news_block}\n"
        f"🤖 AI 심층 분석\n"
        f"{opinion}"
    )

    return answer