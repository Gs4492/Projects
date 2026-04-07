from __future__ import annotations

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class NvidiaClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        self.model = os.getenv(
            "NVIDIA_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1.5"
        )
        self.base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return "NVIDIA API key not configured yet. Using fallback local orchestration response."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 1400,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return f"NVIDIA API returned no choices. Response: {data}"
                message = choices[0].get("message", {})
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

                for fallback_key in ("reasoning_content", "reasoning"):
                    fallback = message.get(fallback_key)
                    if isinstance(fallback, str) and fallback.strip():
                        return fallback.strip()

                return f"NVIDIA API returned no usable text. Response: {data}"
            except httpx.HTTPStatusError as exc:
                body = exc.response.text.strip()
                return (
                    "NVIDIA API request failed, so the app fell back to local orchestration. "
                    f"Status: {exc.response.status_code}. Body: {body}"
                )
            except httpx.RequestError as exc:
                return (
                    "NVIDIA API request failed, so the app fell back to local orchestration. "
                    f"Request error: {type(exc).__name__}: {exc}"
                )
            except Exception as exc:
                return (
                    "NVIDIA API request failed, so the app fell back to local orchestration. "
                    f"Unexpected error: {type(exc).__name__}: {exc}"
                )


nvidia_client = NvidiaClient()
