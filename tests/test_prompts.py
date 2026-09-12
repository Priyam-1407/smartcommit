from smartcommit.prompts import build_commit_prompt


def test_prompt_includes_diff():
    diff = "+ added a line\n- removed a line"
    prompt = build_commit_prompt(diff)
    assert "added a line" in prompt
    assert "removed a line" in prompt


def test_prompt_truncates_long_diff():
    diff = "x" * 10000
    prompt = build_commit_prompt(diff, max_diff_chars=100)
    assert "[diff truncated]" in prompt
    # the full 10000-char diff should NOT appear verbatim in the prompt
    assert "x" * 10000 not in prompt
    # a truncated ~100-char chunk should be present
    assert "x" * 100 in prompt


def test_prompt_no_truncation_note_for_short_diff():
    diff = "short diff"
    prompt = build_commit_prompt(diff, max_diff_chars=6000)
    assert "[diff truncated]" not in prompt
