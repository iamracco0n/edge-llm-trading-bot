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
    timeout=60
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
        "위 데이터에 근거해 단계적으로 분석하라. 규칙:\n"
        "- 반드시 제공된 수치를 근거로 들 것 (추측 금지)\n"
        "- 다음 형식으로 답할 것:\n"
        "  ① 현재 상황 : (추세·모멘텀·거래량 해석)\n"
        "  ② 핵심 근거 : (긍정/부정 요인 각각)\n"
        "  ③ 리스크 : (주의할 점)\n"
        "  ④ 결론 : (매수/보유/관망 중 하나 + 한 줄 이유)\n"
        "- 확신하지 말 것. 투자 조언이 아닌 참고 의견임을 전제."
    )

    return ask_llm(
        prompt,
        max_tokens=768,
        temperature=0.3,
        timeout=120
    )
