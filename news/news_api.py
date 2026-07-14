import json
import requests
import re

with open(
    "/home/user/xavier_nx_ai/secrets/naver_api.json",
    "r",
    encoding="utf-8"
) as f:
    KEY = json.load(f)

CLIENT_ID = KEY["client_id"]
CLIENT_SECRET = KEY["client_secret"]


POSITIVE_WORDS = [
    "증가",
    "확대",
    "성장",
    "호조",
    "개선",
    "최대",
    "상승",
    "흑자",
    "수주",
    "신기록"
]

NEGATIVE_WORDS = [
    "감소",
    "하락",
    "악화",
    "적자",
    "우려",
    "급락",
    "부진",
    "리스크",
    "약세"
]


def get_news(keyword):

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    params = {
        "query": keyword,
        "display": 5,
        "sort": "date"
    }

    try:

        r = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=5
        )

        data = r.json()

        if "items" not in data:

            print("Naver API Error :", data)

            return []

        titles = []

        for item in data["items"]:

            title = re.sub(
                "<.*?>",
                "",
                item["title"]
            )

            titles.append(title)

        return titles

    except Exception as e:

        print("News Error :", e)

        return []


def sentiment_from_titles(news_titles):
    """
    이미 가져온 제목 리스트로 키워드 기반 감성 판정.
    (API 재호출 없음 — 대량 스캔/폴백용. 개별 종목은 LLM 판정을 쓴다.)
    """

    if len(news_titles) == 0:
        return "중립"

    score = 0

    for title in news_titles:

        for word in POSITIVE_WORDS:

            if word in title:
                score += 1

        for word in NEGATIVE_WORDS:

            if word in title:
                score -= 1

    if score > 1:
        return "긍정"

    elif score < -1:
        return "부정"

    else:
        return "중립"


def get_news_sentiment(keyword):
    # 하위호환 유지: 키워드로 뉴스 받아 키워드 기반 감성 반환
    return sentiment_from_titles(get_news(keyword))


def get_news_sentiment_llm(news_titles):
    """
    로컬 LLM이 뉴스 제목을 직접 읽고 감성을 판정한다.
    단어 카운팅과 달리 부정어·맥락을 처리한다.
    반환: "긍정" / "중립" / "부정" (파싱 실패 시 키워드 방식으로 폴백)
    """

    from llm.llm_client import ask_llm

    if len(news_titles) == 0:
        return "중립"

    titles_block = "\n".join(f"- {t}" for t in news_titles)

    prompt = (
        "다음은 한 종목 관련 최신 뉴스 제목이다.\n"
        f"{titles_block}\n\n"
        "이 제목들이 해당 종목 주가에 주는 전반적 분위기를 판단하라. "
        "'적자 우려 해소'처럼 부정어가 뒤집히는 맥락에 유의할 것. "
        "반드시 '긍정' / '중립' / '부정' 중 한 단어로만 답하라."
    )

    answer = ask_llm(prompt, max_tokens=8, temperature=0.0, timeout=90)

    for label in ("긍정", "부정", "중립"):
        if label in answer:
            return label

    # LLM 실패/이상응답 → 키워드 방식 폴백
    return sentiment_from_titles(news_titles)