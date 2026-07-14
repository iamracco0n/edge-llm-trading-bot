import re
import requests

LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"

with open(
"/home/user/xavier_nx_ai/llm/system_prompt.txt",
"r",
encoding="utf-8"
) as f:
    system_prompt = f.read()


def _strip_think(text):

    # Qwen3 등 추론(thinking) 모델이 붙이는 <think>...</think> 블록 제거
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()


def ask_llm(
    prompt,
    max_tokens=192,
    temperature=0.2,
    timeout=150
):

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:

        response = requests.post(
            LLM_URL,
            json=payload,
            timeout=timeout
        )

        answer = response.json()["choices"][0]["message"]["content"]

        return _strip_think(answer)

    except Exception as e:

        print("LLM Error :", e)

        return "LLM 서버에 연결하지 못했습니다."


def deep_analyze(
    title,
    data_lines,
    question
):
    """
    구조화된 데이터를 통째로 먹여서 '추론 기반 분석'을 받는다.
    - title: 분석 대상 (예: "삼성전자", "KRW-BTC")
    - data_lines: "지표명 : 값" 문자열 리스트 (지표·뉴스·포지션 등 전부)
    - question: 시키고 싶은 분석 질문
    """

    data_block = "\n".join(data_lines)

    prompt = (
        f"[분석 대상] {title}\n\n"
        f"[제공 데이터]\n{data_block}\n\n"
        f"[요청]\n{question}\n\n"
        "위 데이터의 수치에 근거해 분석하라(추측 금지). "
        "아래 4항목으로, 각 항목 1~2문장씩 간결하게:\n"
        "① 현재 상황 : 추세·모멘텀 해석\n"
        "② 핵심 근거 : 긍정/부정 요인\n"
        "③ 리스크 : 주의점\n"
        "④ 결론 : 매수/보유/관망 중 하나 + 한 줄 이유\n"
        "확신하지 말 것. 투자 조언 아닌 참고 의견."
    )

    # Xavier는 CPU 추론이라 느림 → 출력은 짧게(간결 프롬프트),
    # 대신 타임아웃은 넉넉히 잡아 완주 보장
    return ask_llm(
        prompt,
        max_tokens=450,
        temperature=0.3,
        timeout=360
    )
