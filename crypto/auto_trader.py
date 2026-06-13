import sys
import time

sys.path.append(
    "/home/user/xavier_nx_ai"
)

from crypto.trade_manager import manage_trade


while True:

    try:

        print(
            "\n===== 자동매매 시작 ====="
        )

        manage_trade()

        print(
            "1시간 대기..."
        )

    except Exception as e:

        print(
            "오류 :",
            e
        )

    time.sleep(
        3600
    )