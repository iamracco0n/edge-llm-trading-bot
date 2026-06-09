import requests

LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"

with open(
"/home/user/xavier_nx_ai/llm/system_prompt.txt",
"r",
encoding="utf-8"
) as f:
    system_prompt = f.read()

def ask_llm(prompt):

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
        "temperature": 0.2,
        "max_tokens": 192
    }

    response = requests.post(
        LLM_URL,
        json=payload
    )

    answer = response.json()["choices"][0]["message"]["content"]

    return answer