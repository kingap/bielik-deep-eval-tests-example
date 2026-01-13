import os
from openai import OpenAI

MODEL = os.getenv("OLLAMA_MODEL", "SpeakLeash/bielik-11b-v3.0-instruct:Q8_0")

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    timeout=180.0,
)

def call_bielik(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()
