from market.us_news import get_us_news
from market.kr_news import get_kr_news
from market.exchange_rate import get_usdkrw
from market.recommend_stock import get_recommend_stocks
from market.recommend_stock_llm import get_llm_recommendations

from llm.llm_client import ask_llm


def create_report():

    us_news = get_us_news()

    kr_news = get_kr_news()

    usdkrw = get_usdkrw()

    # LLM 강화 추천(배치 전용, 느림) → 실패 시 키워드 방식 폴백
    try:
        stocks = get_llm_recommendations()
    except Exception as e:
        print("LLM 추천 실패, 키워드 폴백:", e)
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

    if not stocks:
        report += (
            "오늘은 추천 조건(기술점수 40+)을 만족하는 종목이 없습니다.\n"
            "하락장에선 관망이 상책입니다.\n\n"
        )

    for i, stock in enumerate(
        stocks
    ):

        # LLM 판정 뱃지 (있으면)
        badge = (
            f"  [{stock['verdict']}]"
            if stock.get("verdict") else ""
        )

        report += (

            f"{i+1}. {stock['name']}{badge}\n"

            f"매수 : {stock['buy_price']:,}원\n"

            f"목표 : {stock['target_price']:,}원\n"

            f"손절 : {stock['stop_price']:,}원\n"

        )

        # LLM 심층분석 (있으면)
        if stock.get("analysis"):
            report += f"\n🤖 {stock['analysis']}\n"

        report += "\n"

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