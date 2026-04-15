import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.api_key = None
        try:
            self.api_key = st.secrets.get("PERPLEXITY_API_KEY")
        except Exception:
            self.api_key = None

        if not self.api_key:
            self.api_key = os.getenv("PERPLEXITY_API_KEY")

        self.url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"

    def is_configured(self):
        return bool(self.api_key)

    def generate_json(self, prompt: str):
        if not self.api_key:
            return {"error": "PERPLEXITY_API_KEY is missing"}

        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an e-commerce search refinement assistant. "
                                "Return strict JSON only. "
                                "Do not use markdown code fences."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            start = content.find("{")
            end = content.rfind("}")

            if start == -1 or end == -1:
                return {"error": "No JSON object found", "raw": content}

            json_text = content[start:end + 1]
            parsed = json.loads(json_text)
            return parsed

        except Exception as e:
            return {"error": str(e)}