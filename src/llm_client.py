import json
import os
import streamlit as st
import httpx
from openai import OpenAI

def get_secret(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

class LLMClient:
    def __init__(self):
        self.internal_key = get_secret("JOYLLM_API_KEY") or os.getenv("JOYLLM_API_KEY")
        self.internal_base = get_secret("JOYLLM_BASE_URL") or os.getenv("JOYLLM_BASE_URL")
        self.internal_model = get_secret("JOYLLM_MODEL") or os.getenv("JOYLLM_MODEL", "gemini-2.5-flash-image")

        self.pplx_key = get_secret("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.pplx_base = get_secret("OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.perplexity.ai")
        self.pplx_model = get_secret("OPENAI_MODEL") or os.getenv("OPENAI_MODEL", "sonar-pro")

    def _call_client(self, api_key, base_url, model, prompt, timeout_seconds=12):
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(timeout=timeout_seconds),
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content.strip()
        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found")

        return json.loads(content[start:end + 1])

    def generate_json(self, prompt: str):
        if self.internal_key and self.internal_base:
            try:
                result = self._call_client(
                    self.internal_key,
                    self.internal_base,
                    self.internal_model,
                    prompt,
                    timeout_seconds=8,
                )
                result["_provider"] = "internal"
                return result
            except Exception:
                pass

        if not self.pplx_key:
            return {"error": "Fallback OPENAI_API_KEY is missing"}

        result = self._call_client(
            self.pplx_key,
            self.pplx_base,
            self.pplx_model,
            prompt,
            timeout_seconds=20,
        )
        result["_provider"] = "perplexity"
        return result