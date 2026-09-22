# AGENTS.md — HackAlem AI team rules

## Context
- Hackathon runs 13:00-18:00 (5 hours), Education track. Feature freeze at 16:30.
- The task and the official scoring methodology are published at the start. Update this section with the task summary and every MANDATORY admission condition as soon as they are known.

## How we are scored (Положение, п. 7.4) — technical stage, 100 points
| Criterion | Points | What it means for us |
|---|---|---|
| Case fit & functionality | 20 | Every mandatory requirement of the case works. Main scenario runs fully from input to result. Only working features count. |
| Technical implementation | 25 | Features are really implemented in code, components are connected, structure is clear. Key functions must NOT be replaced by pre-written answers or imitation. |
| README & documentation | 20 | README replaces the presentation. Content matters, not looks. |
| Reproducibility & deployment | 20 | A juror runs it in a clean environment from the README. A deployed link is a bonus, not a substitute. |
| Reliability & security | 15 | Main scenario never crashes on valid input; obviously invalid input is handled gracefully. |
- AI judges may do the preliminary evaluation (п. 8.3): everything must be explicit and easy to verify in the repo and README.
- Extra features do NOT compensate for a missed mandatory condition (п. 7.3).

## Hard rules (Положение)
- The platform repo (edu.astanahub.com) is the ONLY working repo. It locks at 18:00; that snapshot is the competition version for all stages, including Demo Day.
- Verifiable progress EVERY hour, or the team can be disqualified (п. 6.6): commit at least hourly with a meaningful message, and append a line to `PROGRESS.md`.
- Disclose all pre-made material, libraries, models, templates and datasets (п. 6.4) in the README.
- Never commit API keys. Use `.env` (gitignored) and `.env.example`.
- The team repo is a GitHub repo created by the platform. All final code must be pushed there.
- EVERY team member must make a personal, visible contribution (commits under their own GitHub account). Participation is not counted otherwise.
- We solve exactly ONE case from the track.
- README is written in Russian (organisers' template), see the readme-writer skill.

## Prime directive
Mandatory requirements first, working end to end, then documentation and reproducibility. Polish comes last.

## Stack (do not change without the team agreeing)
- Python 3.11+, single repo. Pin versions in `requirements.txt`.
- OpenAI Python SDK. Model from env var `OPENAI_MODEL`, key from `OPENAI_API_KEY` (loaded via `python-dotenv`).
- Budget is $50 of API credits: cheap model while developing, strong model for the final version. Avoid loops with many API calls.
- UI: Streamlit (`app.py`). Logic lives in plain Python modules, not in the UI file.
- Storage: in-memory or local JSON/SQLite. No external services that a juror would need to set up.

## Cross-platform rules (we develop on Windows; jurors likely run Linux/macOS)
- Open every file with `encoding="utf-8"`; Kazakh/Russian text must display correctly.
- Use `pathlib` and relative paths only. Never hardcode `C:\` paths or backslashes.
- No Windows-only commands or packages in the project.
- README gives install/run commands for BOTH Windows (PowerShell) and Linux/macOS.
- Prefer `python -m pip ...`, `python -m streamlit run app.py`, `python -m pytest` (work without venv activation).

## Project layout
```
app.py            # Streamlit UI only — calls agent/
agent/core.py     # agent loop (plan -> tool calls -> check -> answer)
agent/tools.py    # tool functions + their JSON schemas
agent/prompts.py  # all system prompts in one place
data/             # sample/seed data shipped with the repo
tests/            # a few pytest checks of the main scenario and bad input
.env.example      # OPENAI_API_KEY=, OPENAI_MODEL=
PROGRESS.md       # one line per hour: time, what was done
README.md
```

## How to work
- Small, focused changes. One feature per request. The app must start with `streamlit run app.py` after every change.
- Real AI calls are the default. Never hardcode results for the main scenario.
- If the API key is missing or the API fails, show a clear, labelled error or "offline mode" message. Never silently return canned answers as if they were real.
- Validate inputs (empty text, wrong file type, too long, wrong language) and show friendly messages instead of stack traces.
- Log each agent step (tool name, inputs, short result) so the UI can show the reasoning trail.
- Do not delete or rewrite working features unless asked.
- User-facing content supports Kazakh, Russian and English; answer in the user's language.

## Before saying a task is done
1. Run the app or `python -c "import agent.core"`, and `pytest -q` if tests exist.
2. Confirm no secrets are in the code.
3. Summarise in 3 lines what changed and how to test it.
