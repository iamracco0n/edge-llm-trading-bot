"""
1시간봉 추세추종 봇 실행 루프 (페이퍼 모드).

기존 5분봉 봇(auto_trader.py)과 독립 실행.
1시간봉 전략이라 1시간 주기로 점검한다.
"""

import sys
import time

sys.path.append("/home/user/xavier_nx_ai")

from crypto.htf_manager import manage_htf


while True:

    try:
        print("\n===== [HTF] 추세추종 점검 =====")
        manage_htf()
        print("1시간 대기...")

    except Exception as e:
        print("오류 :", e)

    time.sleep(3600)
