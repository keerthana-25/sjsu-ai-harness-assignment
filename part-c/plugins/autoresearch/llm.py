"""Thin OpenRouter chat-completion helper, reusing the client setup proven
in Part A (openai SDK pointed at OpenRouter's OpenAI-compatible endpoint)."""
import os
from openai import OpenAI

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"  # proven reliable in Part B


def generate(system: str, user: str, model: str = DEFAULT_MODEL, temperature: float = 0.8) -> str:
    """Return the raw text of one model completion. Raises on API/auth errors."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    client = OpenAI(base_url=BASE_URL, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=2000,
    )
    # Free-tier models occasionally return choices=None (provider-side hiccup,
    # not an SDK-raised error) instead of a normal completion.
    if not response.choices:
        raise RuntimeError(f"empty response from model {model!r}: {response!r}")
    return response.choices[0].message.content or ""
