---
name: plan-manager
description: "Rosetta skill for plan creation, tracking, and execution coordination via local JSON files."
dependencies: node.js
disable-model-invocation: false
user-invocable: true
argument-hint: feature-name plan-name
allowed-tools: Bash(node:*)
model: claude-sonnet-4.6
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

Primary plan manager for orchestrators and subagents. Creates, tracks, and executes plans as local JSON files.

</when_to_use_skill>

<core_concepts>

- Rosetta prep steps completed
- Plan file lives in FEATURE PLAN folder: `<feature_plan_folder_full_path>/plan.json`
- Helper CLI: `node <plan_manager_full_path>/plan_manager.js <cmd> <feature_plan_folder_full_path>/plan.json [args...]` — no npm install needed
- Always use full absolute paths for both `plan_manager.js` and the plan file
- Seven commands: `help`, `create`, `next`, `update_status`, `show_status`, `query`, `upsert`
- Resume behavior: `next` returns `in_progress` steps first with `resume: true`, then `open` steps with `resume: false`
- Status propagation: bottom-up (steps → phases → plan); plan root is always derived
- ACQUIRE `plan-manager/assets/pm-schema.md` FROM KB for data structure reference

</core_concepts>

<process>

**Setup (every session):**

- If context already contains `RUNNING AS A PLUGIN`: `plan_manager.js` is already available at `<skill_base_dir>/assets/plan_manager.js` — execute directly, no copy needed
- Otherwise: ACQUIRE `plan-manager/assets/plan_manager.js` FROM KB → write to AGENTS TEMP folder

**Orchestrator flow:**

1. Create plan: `node <plan_manager_full_path>/plan_manager.js create <feature_plan_folder_full_path>/plan.json <json>` — see pm-schema.md for JSON structure
2. Upsert phases and steps: `node <plan_manager_full_path>/plan_manager.js upsert <feature_plan_folder_full_path>/plan.json entire_plan <json>`
3. Delegate steps to subagents — pass plan file path and step IDs
4. Loop: call `next` until `plan_status: complete` and `count: 0`

**Subagent flow:**

1. Get next steps: `node <plan_manager_full_path>/plan_manager.js next <feature_plan_folder_full_path>/plan.json [limit]`
2. Check `resume` flag — if `true`, continue interrupted work; if `false`, start fresh
3. Execute step
4. Update: `node <plan_manager_full_path>/plan_manager.js update_status <feature_plan_folder_full_path>/plan.json <step-id> complete`
5. Repeat from step 1

</process>

<validation_checklist>

- `node <plan_manager_full_path>/plan_manager.js help` exits without error
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
