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


def get_kr_news():

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    params = {
        "query": "코스피",
        "display": 3,
        "sort": "date"
    }

    r = requests.get(
        url,
        headers=headers,
        params=params
    )

    items = r.json()["items"]

    news = []

    for item in items:

        title = re.sub("<.*?>", "", item["title"])

        news.append(title)

    return news