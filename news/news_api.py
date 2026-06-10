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
        "display": 3,
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


def get_news_sentiment(keyword):

    news_titles = get_news(keyword)

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