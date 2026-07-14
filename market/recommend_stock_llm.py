"""
아침 종목 추천 — LLM 강화판 (배치 전용, CPU LLM).

대화형이 아니라 cron 배치라 느려도 됨 → LLM을 깊게 쓴다.
깔때기: 기술스캔 189 → 상위 N_TECH → LLM 3회투표 판정 → 상위 N_FINAL → 심층분석.

각 LLM 콜은 실패해도 전체가 죽지 않도록 방어(키워드/기술점수 폴백).
"""

import json
import numpy as np
import yfinance as yf

from news.news_api import get_news
from llm.llm_client import deep_analyze


with open(
    "/home/user/xavier_nx_ai/stock/stocks.json",
    "r",
    encoding="utf-8"
) as f:
    STOCKS = json.load(f)


# ===== 역할 분담 =====
# 숫자(규칙)가 종목을 고르고, LLM은 최종 후보를 '설명 + 악재 체크'만 한다.
# (작은 3B 모델에 랭킹 같은 무리한 판단은 안 시킴)
N_TECH = 8      # 기술 스캔 상위 (여유분)
N_FINAL = 3     # 최종 추천 (LLM 심층분석 대상)
MIN_SCORE = 40  # 이 점수 미만은 추천 안 함 (하락장엔 추천 0개도 정상)


# =====================================================
# 차트 흐름을 텍스트로 인코딩 (텍스트 LLM이 '모양'을 읽게)
# =====================================================
def chart_features(df):

    close = df["Close"].values.flatten().astype(float)
    high = df["High"].values.flatten().astype(float)
    low = df["Low"].values.flatten().astype(float)
    vol = df["Volume"].values.flatten().astype(float)

    cur = close[-1]

    def ret(n):
        return (cur / close[-1 - n] - 1) * 100 if len(close) > n else 0.0

    r1w, r1m = ret(5), ret(20)
    r3m = (cur / close[0] - 1) * 100

    hi3, lo3 = high.max(), low.min()
    pos = (cur - lo3) / (hi3 - lo3) * 100 if hi3 > lo3 else 50.0

    ma20 = np.mean(close[-20:])
    ma60 = np.mean(close[-60:]) if len(close) >= 60 else np.mean(close)
    dev20 = (cur / ma20 - 1) * 100
    align = "정배열(단기>장기)" if ma20 > ma60 else "역배열(단기<장기)"

    diffs = np.diff(close[-11:])          # 최근 10일 변화
    up_days = int((diffs > 0).sum())
    last_dir = "상승" if close[-1] >= close[-2] else "하락"

    n = min(20, len(close))
    vola = np.mean((high[-n:] - low[-n:]) / close[-n:]) * 100

    v5 = np.mean(vol[-5:])
    v20 = np.mean(vol[-20:])
    volr = (v5 / v20 * 100) if v20 else 100.0

    idx = np.linspace(0, len(close) - 1, 8).astype(int)
    path = " → ".join(f"{close[i] / 1000:.0f}k" for i in idx)

    return [
        "[차트 흐름]",
        f"  수익률 : 1주 {r1w:+.1f}% / 1개월 {r1m:+.1f}% / 3개월 {r3m:+.1f}%",
        f"  이동평균 : {align}, 현재가 MA20 대비 {dev20:+.1f}%",
        f"  3개월 범위 내 위치 : {pos:.0f}% (0=저점, 100=천장)",
        f"  최근 10일 중 상승 {up_days}일, 직전봉 {last_dir}",
        f"  변동성(일 변동폭 평균) : {vola:.1f}%",
        f"  거래량 : 최근5일이 20일평균의 {volr:.0f}%",
        f"  가격경로(3개월→현재) : {path}",
    ]


# =====================================================
# ① 기술 스캔 (빠름) — 국내 종목 지표 계산 + 점수
# =====================================================
def _score_one(name, ticker, df):
    """단일 종목 df(단일레벨 컬럼)로 지표·점수 계산 → 후보 dict (또는 None)."""

    df = df.dropna()
    if len(df) < 60:
        return None

    close = df["Close"]
    current = float(close.iloc[-1])
    ma20 = float(close.rolling(20).mean().iloc[-1])
    ma60 = float(close.rolling(60).mean().iloc[-1])
    high = float(df["High"].max())

    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    rsi = float((100 - (100 / (1 + rs))).iloc[-1])

    vol_now = float(df["Volume"].iloc[-1])
    vol_avg = float(df["Volume"].rolling(20).mean().iloc[-1])
    vol_ratio = vol_now / vol_avg if vol_avg else 0

    score = 0

    if current > ma20 > ma60:
        score += 40
        trend = "상승"
    elif current > ma60:
        score += 20
        trend = "횡보"
    else:
        score -= 20
        trend = "하락"

    if 40 <= rsi <= 65:
        score += 20
    elif 30 <= rsi <= 70:
        score += 10
    if rsi >= 75:
        score -= 20      # 과매수 구간 감점

    if vol_ratio > 1.5:
        score += 20
    elif vol_ratio > 1:
        score += 10

    return {
        "name": name,
        "ticker": ticker,
        "current": int(current),
        "ma20": int(ma20),
        "ma60": int(ma60),
        "high": int(high),
        "rsi": int(rsi),
        "vol_ratio": round(vol_ratio, 2),
        "trend": trend,
        "tech_score": score,
        "chart": chart_features(df),
    }


def technical_scan():
    # yfinance 레이트리밋 회피 → 배치(청크) 다운로드로 전체 유니버스 커버
    pairs = [
        (n, t) for n, t in STOCKS.items()
        if ".KS" in t or ".KQ" in t
    ]
    name_by = {t: n for n, t in pairs}
    tickers = [t for _, t in pairs]

    candidates = []
    CHUNK = 50

    for i in range(0, len(tickers), CHUNK):
        chunk = tickers[i:i + CHUNK]
        try:
            data = yf.download(
                chunk, period="3mo", group_by="ticker",
                progress=False, threads=True
            )
        except Exception:
            continue

        for ticker in chunk:
            try:
                df = data[ticker]      # 배치 → data[티커]가 단일레벨 OHLCV
                c = _score_one(name_by[ticker], ticker, df)
                if c is not None:
                    candidates.append(c)
            except Exception:
                continue

    candidates.sort(
        key=lambda x: (x["tech_score"], x["vol_ratio"]),
        reverse=True
    )
    return candidates[:N_TECH]


# =====================================================
# 데이터 → LLM 입력용 라인
# =====================================================
def build_data_lines(c, titles):
    rsi = c["rsi"]
    # 작은 모델이 숫자를 오독하지 않게 상태를 미리 떠먹여줌
    rsi_state = (
        "과매수" if rsi >= 70
        else "과매도" if rsi <= 30
        else "중립"
    )
    lines = [
        f"현재가 : {c['current']:,}원",
        f"MA20 : {c['ma20']:,}원 / MA60 : {c['ma60']:,}원",
        f"3개월 최고가 : {c['high']:,}원",
        f"RSI(14) : {rsi} ({rsi_state})",
        f"차트 추세 : {c['trend']}",
    ]

    # 차트 흐름(궤적) 추가 — 스냅샷이 아니라 '모양'을 읽게
    if c.get("chart"):
        lines.extend(c["chart"])

    lines.append("최근 뉴스 :")

    if titles:
        for t in titles[:5]:
            lines.append(f"  - {t}")
    else:
        lines.append("  - (뉴스 없음)")
    return lines


# =====================================================
# deep_analyze 결과에서 결론(매수/보유/관망) 추출
# =====================================================
def extract_verdict(text):
    # deep_analyze는 "④ 결론 : 매수/보유/관망 ..." 형식으로 끝난다
    if not text:
        return None
    tail = text.split("결론", 1)[-1]     # 결론 이후에서만 탐색
    best, best_idx = None, 999
    for label in ("매수", "보유", "관망"):
        i = tail.find(label)
        if i != -1 and i < best_idx:
            best_idx, best = i, label
    return best


# =====================================================
# 전체 파이프라인
# =====================================================
def get_llm_recommendations():

    # ① 숫자(규칙)가 종목을 고른다 — 하한선 통과분 중 상위 N_FINAL
    #    (억지로 3개 채우지 않음. 하락장엔 0개도 정상)
    ranked = technical_scan()
    finalists = [c for c in ranked if c["tech_score"] >= MIN_SCORE][:N_FINAL]

    # ② LLM은 최종 후보만 '차트·뉴스 읽고 설명 + 악재 체크'
    for c in finalists:
        titles = get_news(c["name"])
        c["news"] = titles

        c["buy_price"] = min(c["current"], c["ma20"])

        # 목표가 = 현재가 기준 추세별 현실적 상단 (과거 고점 아님)
        tp_mult = (
            1.10 if c["trend"] == "상승"
            else 1.07 if c["trend"] == "횡보"
            else 1.05
        )
        c["target_price"] = int(c["current"] * tp_mult)
        c["stop_price"] = int(c["current"] * 0.93)

        try:
            analysis = deep_analyze(
                title=c["name"],
                data_lines=build_data_lines(c, titles),
                question=(
                    "이 종목을 오늘 매수 후보로 볼지 지표·차트흐름·뉴스를 "
                    "근거로 분석하라. 특히 뉴스에 명백한 악재가 있으면 반드시 "
                    "짚고 결론을 보수적으로 낮춰라. 핵심 이유와 리스크를 "
                    "서술하고, ④ 결론은 매수/보유/관망 중 하나로 내려라."
                )
            )
            c["analysis"] = analysis
            # 결론(매수/보유/관망) 뱃지 — 실패 시 추세로 폴백
            c["verdict"] = extract_verdict(analysis) or c["trend"]
        except Exception:
            c["analysis"] = "(심층분석 생성 실패)"
            c["verdict"] = None

    return finalists


if __name__ == "__main__":
    import time

    t0 = time.time()
    recs = get_llm_recommendations()
    for i, c in enumerate(recs):
        print(f"\n{'='*40}")
        print(f"{i+1}. {c['name']}  [{c.get('verdict')}]  (기술점수 {c['tech_score']})")
        print(f"   매수 {c['buy_price']:,} / 목표 {c['target_price']:,} "
              f"/ 손절 {c['stop_price']:,}")
        print(f"   {c.get('analysis','')[:300]}")
    print(f"\n--- 총 {time.time()-t0:.0f}초 ---")
