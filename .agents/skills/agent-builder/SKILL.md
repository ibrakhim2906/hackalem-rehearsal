---
name: agent-builder
description: Build or extend the tool-using AI agent (agent loop, tools, prompts) with the OpenAI API. Use whenever the task involves making the AI plan steps, call functions/tools, use data, or check its own output.
---

# Agent builder

Goal: a small, reliable agent that visibly *does things*, not a plain chatbot.

## Pattern (keep this shape)
1. **Input**: user request + any context (student profile, uploaded text, task data).
2. **Plan**: model decides which tools to call.
3. **Act**: call tools via the OpenAI tools / function-calling interface; loop until the model returns a final answer. Cap the loop at ~6 steps.
4. **Check**: one self-review pass: "Does this answer the request, is it accurate, is it in the user's language?" Fix if not.
5. **Output**: structured result for the UI plus the list of steps taken.

## Tools
- Each tool = one plain Python function in `agent/tools.py` + its JSON schema next to it.
- Keep tools deterministic where possible (lookups, calculations, scoring, saving) so the demo is stable.
- Typical education tools: `get_student_profile`, `generate_quiz`, `grade_answers`, `build_study_plan`, `search_materials`, `save_progress`, `schedule_reminder`.
- Tools return small JSON dicts, never huge text blobs.

## Structured output
- When the UI needs fields (scores, plan items, questions), ask the model for JSON with a clear schema and validate it. On parse failure retry once, then fall back to a safe default.

## Prompts
- All system prompts live in `agent/prompts.py`.
- Each system prompt states: role, target user, allowed tools, output format, language rule, "be concise".

## Done when
- One full run works end to end from the UI, and the step log shows at least 2 tool calls.
