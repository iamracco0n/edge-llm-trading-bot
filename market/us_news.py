import feedparser


def get_us_news():

    url = "https://finance.yahoo.com/news/rssindex"

    feed = feedparser.parse(url)

    news = []

    for entry in feed.entries:

        news.append(entry.title)

    return news[:3]