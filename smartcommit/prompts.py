"""
Prompt templates for generating commit messages.
Kept separate from llm.py so you can iterate on wording without
touching API-calling logic -- and so you can unit test prompt building.
"""

COMMIT_MESSAGE_SYSTEM_PROMPT = """You are a senior software engineer who writes precise, \
Conventional Commits messages.

Rules you must follow strictly:
1. Output EXACTLY ONE commit message, nothing else. No explanations, no markdown, no quotes.
2. Format: <type>(<scope>): <description>
   - type is one of: feat, fix, docs, style, refactor, perf, test, chore, build, ci
   - scope is a short lowercase word for the affected area (optional if unclear)
   - description is imperative mood, lowercase start, no trailing period, under 72 chars
3. If the diff touches multiple unrelated things, pick the MOST significant change.
4. Never invent details not present in the diff.
5. If the diff is trivial (whitespace, formatting only), use type "style" or "chore".
"""


def build_commit_prompt(diff: str, max_diff_chars: int = 6000) -> str:
    """
    Builds the full prompt sent to the LLM, given a git diff.
    Truncates very long diffs so we stay within reasonable token limits.
    """
    truncated = diff[:max_diff_chars]
    if len(diff) > max_diff_chars:
        truncated += "\n...[diff truncated]..."

    return f"""{COMMIT_MESSAGE_SYSTEM_PROMPT}

Here is the git diff of staged changes:

```
{truncated}
```

Respond with only the commit message, one line."""
