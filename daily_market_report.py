from market.us_news import get_us_news
from market.kr_news import get_kr_news
from market.exchange_rate import get_usdkrw
from market.recommend_stock import get_recommend_stocks

from llm.llm_client import ask_llm


def create_report():

    us_news = get_us_news()

    kr_news = get_kr_news()

    usdkrw = get_usdkrw()

    stocks = get_recommend_stocks()

    # =====================
    # AI 코멘트
    # =====================

    prompt = f"""
    미국 뉴스:
    {us_news}

    한국 뉴스:
    {kr_news}

    위 뉴스들을 종합했을 때 현재 시장 분위기만 한 문장으로 표현하라.

    절대 뉴스 내용을 반복하지 말 것.
    절대 번호를 붙이지 말 것.
    설명 금지.

    예시:

    위험자산 선호 심리가 강화되며 대형주 중심 강세가 기대됩니다.

    답:
    """

    try:

        comment = ask_llm(
            prompt
        )

        comment = (
            comment
            .replace(
                "\n",
                " "
            )
            .strip()
        )

    except:

        comment = (
            "변동성 확대에 대비한 분산 대응이 필요해 보입니다."
        )

    # =====================
    # 브리핑 작성
    # =====================

    report = (
        "🌞 오늘의 시장 브리핑\n\n"
    )

    report += (
        "🇺🇸 미국 주요 뉴스\n"
    )

    for news in us_news:

        report += (
            f"• {news}\n"
        )

    report += (
        "\n🇰🇷 국내 주요 뉴스\n"
    )

    for news in kr_news:

        report += (
            f"• {news}\n"
        )

    report += (
        f"\n💵 USD/KRW : {usdkrw}\n\n"
    )

    report += (
        "📈 오늘의 추천 종목\n\n"
    )

    for i, stock in enumerate(
        stocks
    ):

        report += (

            f"{i+1}. {stock['name']}\n"

            f"매수 : {stock['buy_price']:,}원\n"

            f"목표 : {stock['target_price']:,}원\n"

            f"손절 : {stock['stop_price']:,}원\n\n"

        )

    report += (
        "📝 AI 코멘트\n"
    )

    report += (
        comment
    )

    return report


if __name__ == "__main__":

    print(
        create_report()
    )