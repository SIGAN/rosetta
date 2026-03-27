---
name: plan-manager
description: "Rosetta skill for plan creation, tracking, and execution coordination via local JSON files when plan_manager MCP is unavailable."
dependencies: node.js
disable-model-invocation: false
user-invocable: true
argument-hint: plan-name
allowed-tools: Bash(node:*)
model: claude-sonnet-4-6, gpt-5.4-medium, gemini-3.1-pro-preview
tags:
  - plan-manager
  - plan-manager-create
  - plan-manager-use
baseSchema: docs/schemas/skill.md
---

<plan-manager>

<role>

Senior execution planner and tracker for plan-driven workflows.

</role>

<when_to_use_skill>

Use when `plan_manager` MCP tool is unavailable. Provides local JSON fallback with identical command semantics for both orchestrators and subagents.

</when_to_use_skill>

<core_concepts>

- Rosetta prep steps completed
- Plan file convention: `plans/<plan-name>/plan.json`
- Helper CLI: `node agents/TEMP/plan_manager.js <cmd> <plan-file> [args...]` — no npm install needed
- Seven commands: `help`, `create`, `next`, `update_status`, `show_status`, `query`, `upsert`
- Resume behavior: `next` returns `in_progress` steps first with `resume: true`, then `open` steps with `resume: false`
- Status propagation: bottom-up (steps → phases → plan); plan root is always derived
- ACQUIRE `plan-manager/assets/pm-schema.md` FROM KB for data structure reference

</core_concepts>

<process>

**Setup (every session):**

1. ACQUIRE `plan-manager/assets/plan_manager.js` FROM KB → write to `agents/TEMP/plan_manager.js`

**Orchestrator flow:**

1. Create plan: `node agents/TEMP/plan_manager.js create plans/<name>/plan.json <json>` — see pm-schema.md for JSON structure
2. Upsert phases and steps: `node agents/TEMP/plan_manager.js upsert plans/<name>/plan.json entire_plan <json>`
3. Delegate steps to subagents — pass plan file path and step IDs
4. Loop: call `next` until `plan_status: complete` and `count: 0`

**Subagent flow:**

1. Get next steps: `node agents/TEMP/plan_manager.js next plans/<name>/plan.json [limit]`
2. Check `resume` flag — if `true`, continue interrupted work; if `false`, start fresh
3. Execute step
4. Update: `node agents/TEMP/plan_manager.js update_status plans/<name>/plan.json <step-id> complete`
5. Repeat from step 1

</process>

<validation_checklist>

- `node agents/TEMP/plan_manager.js help` exits without error
- `show_status` output: plan root status is derived (never manually set)
- `next` output: `in_progress` steps appear before `open` steps when both exist
- `show_status` phase status matches aggregate of its steps after `update_status`

</validation_checklist>

<pitfalls>

- Not checking `resume` flag on `next` results — causes duplicate work on resumed sessions
- Forgetting `update_status` after step completion — plan remains stale
- Plan root status cannot be set directly — it is always derived from phases

</pitfalls>

<resources>

- Asset: ACQUIRE `plan-manager/assets/pm-schema.md` FROM KB — plan JSON structure
- Flow: USE FLOW `adhoc-flow-with-plan-manager`

</resources>

</plan-manager>
