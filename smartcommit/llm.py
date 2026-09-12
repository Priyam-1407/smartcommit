"""
Wraps the Gemini API call. Kept thin and provider-agnostic on purpose --
generate_commit_message() is the only function the rest of the app calls,
so swapping Gemini for Groq/OpenAI later means editing only this file.
"""

import re
from google import genai

from smartcommit.config import Config
from smartcommit.prompts import build_commit_prompt


def _clean_message(raw: str) -> str:
    """
    LLMs sometimes wrap output in markdown code fences or quotes.
    Strip that so we get a clean one-liner.
    """
    text = raw.strip()
    # remove ```lang ... ``` fences if present
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    # remove surrounding quotes
    text = text.strip("\"'`")
    # take only the first non-empty line (guard against multi-line replies)
    lines = [l for l in text.splitlines() if l.strip()]
    return lines[0].strip() if lines else text


def generate_commit_message(diff: str, config: Config) -> str:
    """
    Sends the diff to Gemini and returns a clean Conventional Commits message.
    Raises RuntimeError on API failure.
    """
    client = genai.Client(api_key=config.gemini_api_key)
    prompt = build_commit_prompt(diff, config.max_diff_chars)

    try:
        response = client.models.generate_content(
            model=config.model_name,
            contents=prompt,
        )
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}")

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return _clean_message(response.text)
