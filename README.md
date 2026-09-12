# SmartCommit

A CLI tool that reads your staged Git diff and generates a clean
[Conventional Commits](https://www.conventionalcommits.org/) message using
an LLM (Google Gemini, free tier).

```
$ git add .
$ smartcommit

Analyzing staged diff...
╭─ Suggested commit message ─────────────────────╮
│ feat(auth): add JWT-based login endpoint       │
╰─────────────────────────────────────────────────╯
[Y]es / [E]dit / [N]o: y
Committed (a1b2c3d): feat(auth): add JWT-based login endpoint
```

## Why

Most commit messages are lazy ("fix", "updates", "asdf"). SmartCommit reads
what actually changed and writes a proper, conventional message for you --
in about 2 seconds, for free.

## Install

```bash
pip install smartcommit-cli
```

(or, for local development, see below)

## Setup

1. Get a free Gemini API key from https://aistudio.google.com/apikey
2. Set it as an environment variable, or put it in a `.env` file in your
   project root, or in `~/.smartcommit.toml`:

```
GEMINI_API_KEY=your_key_here
```

## Usage

```bash
git add .
smartcommit              # interactive: shows message, asks Y/E/N
smartcommit --yes        # auto-accept, no prompt
smartcommit --dry-run    # just print the message, don't commit
```

## Local development

```bash
git clone https://github.com/yourname/smartcommit
cd smartcommit
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
pip install -e ".[dev]"
cp .env.example .env            # then add your real key
```

Run tests:

```bash
pytest
```

Run without installing:

```bash
python -m smartcommit.cli
```

## Architecture

```
smartcommit/
├── cli.py         # Typer entry point, user interaction
├── git_utils.py   # reads staged diff, performs commit (GitPython)
├── llm.py         # calls Gemini, cleans response
├── prompts.py     # prompt template, diff truncation
└── config.py      # loads API key from env / .env / ~/.smartcommit.toml
```

Each module has one job and is independently unit tested (`tests/`).
The LLM layer (`llm.py`) is deliberately thin and isolated so a different
provider (Groq, OpenAI) can be swapped in by editing one file.

## Config file (optional)

`~/.smartcommit.toml`:

```toml
gemini_api_key = "your_key_here"
model_name = "gemini-2.0-flash"
max_diff_chars = 6000
```

## License

MIT
