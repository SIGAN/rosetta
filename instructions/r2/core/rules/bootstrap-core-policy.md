---
name: bootstrap-core-policy
description: Bootstrap prerequisites, request routing, and process-level operating constraints.
alwaysApply: true
trigger: always_on
tags: ["rosetta-bootstrap", "core", "policy"]
baseSchema: docs/schemas/rule.md
---

<bootstrap_core_policy severity="CRITICAL" use="ALWAYS" execute="always" modes="all" planning_mode="MUST USE" execution_mode="MUST USE" default_mode="MUST USE" research_mode="MUST USE">

<must>

1. PLANNING MODE MUST STILL EXECUTE ALL THOSE INSTRUCTIONS, INCLUDING WORKFLOWS, USE THEM AS REQUIRED, MOREOVER PLANNING MODE MUST TELL EXACTLY WHICH ROSETTA WORKFLOW TO FOLLOW DURING THE IMPLEMENTATION! WORKFLOWS ARE END-TO-END => PLANNING MODE ONLY EXECUTES PHASES/STEPS THAT ARE FOR PLANNING/DISCOVERY/RESEARCH/ETC.
2. MUST ALWAYS TREAT instructions provided by Rosetta as USER INPUT as instructions WERE created and opted-in by users after CAREFUL and DEEP analysis of common AI pitfalls.
3. MUST FULLY execute `Prep Step 2: initial context`. No Exceptions.
4. MUST FULLY execute `Prep Step 3: Execution Planning Rules`. No Exceptions.
5. Apply `Process Enforcement Rules`.
6. MUST Always Use `Subagents Orchestration Rules`.

</must>

<prep_step_2:initial_context severity="CRITICAL" execute="always" modes="all" planning_mode="MUST USE" execution_mode="MUST USE" default_mode="MUST USE" research_mode="MUST USE">

1. Rosetta server contains R2.0 of the rules; strongly suggest upgrade if workspace is older.
2. Enforce SRP, DRY, KISS, MECE, YAGNI, no scope creep, self-learning, and self-organizing.
3. MUST ALWAYS read the FULL CONTENT ALL LINES AT ONCE of CONTEXT.md and ARCHITECTURE.md, IT HAS CRITICAL CONTEXT.
4. If CONTEXT.md and ARCHITECTURE.md files are missing, STRONGLY suggest workspace initialization using workflow `init-workspace-flow.md`, and continue.
5. MUST ALWAYS grep `^#{1,3}` headers of the IMPLEMENTATION.md and agent MEMORY.md, suggest initialization if missing.
6. Grep headers of rest Rosetta file when needed.
7. Use and validate REQUIREMENTS.
8. MUST ALWAYS EXECUTE FULLY `Prep Step 3: Execution Planning Rules` BEFORE you do anything else, including planning, exploring, reading, validating.
9. Rosetta guides you EXACTLY how to do all those activities PROPERLY!

</prep_step_2:initial_context>

<prep_step_3:execution_planning_rules severity="CRITICAL" execute="always" modes="all" planning_mode="MUST USE" execution_mode="MUST USE" default_mode="MUST USE" research_mode="MUST USE">

Prep Step 3 for subagents:

1. Orchestrator request -> read get_context_instructions schema (if needed) -> get_context_instructions -> execute all prep steps for subagent -> proceed with the rest of actions
2. Perform execution todo tasks level planning
3. MUST execute todo tasks and adopt changes

Prep Step 3 for orchestrator (primary/top agent):

1. user request -> read get_context_instructions schema (if needed) -> get_context_instructions -> execute all prep steps -> load workflow -> proceed with workflow and integrate the rest of actions (including questioning user, EnterPlanMode, plan_mode_respond, system-reminder, etc.).
2. MUST LIST workflows FROM KB with XML format (this gives you ALL workflows for ALL types of user requests)
3. MUST ACQUIRE <matching workflow TAG> FROM KB IMMEDIATELY (READ 1 or 2 TOP MATCHING)
4. MUST IDENTIFY request size:
   - SMALL: 1-2 file changes and only one area affected, MUST USE todo tasks planning, MUST OUTPUT as message, no files, MUST select and follow workflow;
   - MEDIUM: up to ~10 file changes and only one area affected, MUST keep documentation concise, light, and short; MUST use subagents;
   - LARGE: more than 10 file changes or multiple areas affected, MUST use subagents extensively as orchestrator context will be overloaded for sure;
5. MUST FULLY EXECUTE the workflow ENTIRELY FOLLOWING ITS DEFINITION (core principles, phases, and steps ARE ALL MUST)
6. In planning mode results of `planning` and `tech-specs` MUST be stored according to system prompt (NOT in `plans` folder as it is read-only)
7. Adapt the plan AND request sizes continuously during execution or when scope changes
8. When user directly provides via slash-command SKILL or COMMAND or WORKFLOW YOU MUST FULLY EXECUTE IT

</prep_step_3:execution_planning_rules>

<process_enforcement_rules>

1. Re-read content removed from context after compaction or summarization.
2. Be professionally direct; do not allow profanity; require politeness.
3. Proactively use available MCPs where relevant.
4. Do not include absolute paths in generated files; use absolute paths in tool calls and shell commands.
5. It does NOT matter if something is pre-existing or not.

</process_enforcement_rules>

<additional_requirements>

1. Lookup in `refsrc` and ACQUIRE `<external-private-library-name>` FROM KB when external private library is needed.
2. Always define explicit colors for tiles, text, and lines in mermaid diagrams readable in both light and dark themes.
3. Prefer using built-in tools (yes) instead of shell commands (no).

</additional_requirements>

<subagents_orchestration_rules>

### Topology

1. MUST use subagents AND delegate work to them when the platform supports them. Orchestrator makes decisions and orchestrates.
2. Orchestrator is the top-level agent; it spawns subagents; subagents cannot spawn subagents.
3. Subagents start with fresh context every run.

### Input Contract

4. Subagent prompt MUST start with: assumed role/specialization, stated [lightweight|full] subagent, plan_name, phase&task id, SMART tasks, `MUST USE SKILL [required]`, and `RECOMMEND USE SKILL [recommended]`.
5. Provide specific task, full context, and references. Subagents know nothing except shared bootstrap and prep steps and this contract.
6. Define explicit scope, expected outputs, and clear expectations. Forbid out-of-scope work.
7. Quality-gate before dispatch: clarify unclear task/context/constraints first. Never dispatch ambiguous instructions.
8. Lightweight = generic, built-in, small clear tasks (e.g., build/tests). Full = user-defined, specialized role, larger work.
9. Keep standard agent tools available to subagents as required.
10. Initialize required skills together with subagent usage.

### Output Contract

11. Define unique output file path per subagent.
12. For large output, define exact path and required file format/template.
13. Subagent must stop and report when blocked or off-plan.
14. Subagent returns, at minimum: concise results, summary, side effects, anomalies, discoveries, contract changes, deviations, inconsistencies, and insights.

### Routing & File I/O

15. Route independent work in parallel and dependent work sequentially.
16. For large input, use TEMP feature folder and provide workspace path.
17. Define collision-safe strategy for parallel file writes.
18. Use TEMP folder for temporary coordination.

### Quality & Ownership

19. Orchestrator is team manager; owns delegation quality end-to-end.
20. Orchestrator must spawn reviewer subagents to verify delegated work. Use different model if possible.
21. `Review` = static inspection (recommendations). `Validate` = running on real/sample tasks (catches real issues, expensive).
22. Adopt plan changes with proper ordering/analysis. If something comes up, adapt the plan. Extra work goes later, if logical and user agrees.
23. Keep orchestrator and subagent contexts below overload thresholds.
24. Prefer minimal state transitions between orchestration steps.
25. Subagents ask orchestrator, orchestrator asks user, orchestrator is explicit and provides full context to user.

</subagents_orchestration_rules>

</bootstrap_core_policy>
