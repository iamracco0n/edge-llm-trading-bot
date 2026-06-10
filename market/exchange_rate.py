import requests


def get_usdkrw():

    url = "https://open.er-api.com/v6/latest/USD"

    r = requests.get(url)

    data = r.json()

    usdkrw = round(data["rates"]["KRW"], 2)

    return usdkrw