import os
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


class LLMClient:
    def __init__(self):
        self.api_key = get_secret("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = get_secret("OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        self.model = get_secret("OPENAI_MODEL") or os.getenv("OPENAI_MODEL", "gemini-2.5-flash-image")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is missing")
        if not self.base_url:
            raise ValueError("OPENAI_BASE_URL is missing")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def is_configured(self):
        return bool(self.api_key and self.base_url)

    def generate_json(self, prompt: str):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an e-commerce search refinement assistant. Return strict JSON only. Do not use markdown code fences.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
            )

            content = response.choices[0].message.content.strip()
            start = content.find("{")
            end = content.rfind("}")

            if start == -1 or end == -1:
                return {"error": "No JSON object found", "raw": content}

            return json.loads(content[start:end + 1])

        except Exception as e:
            return {"error": str(e)}