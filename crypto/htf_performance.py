"""
1시간봉 추세추종 봇(페이퍼) 성과 모니터.
  실행: venv/bin/python crypto/htf_performance.py
"""

import json

LOG_FILE = "/home/user/xavier_nx_ai/crypto/trade_log_htf.json"
POS_FILE = "/home/user/xavier_nx_ai/crypto/position_htf.json"


def _load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
            return json.loads(data) if data.strip() else default
    except Exception:
        return default


def show():
    logs = _load(LOG_FILE, [])
    pos = _load(POS_FILE, {})

    print("===== HTF 추세추종 성과 (페이퍼) =====")
    print("현재 보유:", list(pos.keys()) if pos else "없음 (현금)")

    if not logs:
        print("청산된 거래 없음 (누적 대기중)")
        return

    profits = [x["profit"] for x in logs]
    wins = [p for p in profits if p > 0]
    n = len(profits)

    print(f"총 청산 : {n}")
    print(f"승률 : {len(wins)/n*100:.1f}%  ({len(wins)}승 {n-len(wins)}패)")
    print(f"평균 수익(승) : {sum(wins)/len(wins):+.2f}%" if wins else "승 없음")
    losses = [p for p in profits if p <= 0]
    if losses:
        print(f"평균 손실(패) : {sum(losses)/len(losses):+.2f}%")
    print(f"누적 손익 : {sum(profits):+.2f}%")
    print(f"실현손익(5만/회) : {sum(p/100*50000 for p in profits):+,.0f}원")
    print(f"최고 : {max(profits):+.2f}%  |  최저 : {min(profits):+.2f}%")

    print("\n최근 청산 5건:")
    for x in logs[-5:]:
        print(f"  {x['ticker']:<12} {x['profit']:+6.2f}%  "
              f"{x.get('hold_hours', 0):>5.1f}h  {x['reason']}")


if __name__ == "__main__":
    show()
