import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PERPLEXITY_API_KEY")
if not api_key:
    raise ValueError("PERPLEXITY_API_KEY is missing from .env")

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": "Reply with exactly: PERPLEXITY_OK"}
        ],
        "temperature": 0
    },
    timeout=30
)

response.raise_for_status()
data = response.json()
print(data["choices"][0]["message"]["content"])