---
name: init-workspace-flow-questions
description: "Phase 7 of init-workspace-flow, contains reflective gap-filling, user verification, and file updates."
tags: ["init", "workspace", "questions", "hitl", "phase"]
baseSchema: docs/schemas/phase.md
---

<init_workspace_flow_questions>

<description_and_purpose>

Problem: Automated analysis leaves gaps — ambiguous domain logic, unstated conventions, missing rationale.
Validation: Every accumulated gap has a resolution; each answer traces to at least one file update.

</description_and_purpose>

<workflow_context>

- Phase 7 of 8 in init-workspace-flow
- Input: all docs from Phases 1–6, accumulated gaps from state
- Output: answers integrated into docs, affected files updated via subagents

</workflow_context>

<phase_steps>

1. Read state and accumulated gaps
2. Review all created docs for gaps and contradictions
3. Ask user reflective questions (bootstrap-hitl-questioning rules)
4. Map answers to affected files
5. Spawn one built-in subagent per affected file: answer content, target path, update instructions, preserve-human-content
6. Verify subagent updates
7. Prompt for optional LSP installation (see lsp_prompt section)
8. Update state — clear resolved gaps, note unresolved, record LSP decision

</phase_steps>

<lsp_prompt step="7" optional="true">

LSP servers provide AI coding agents with IDE-grade intelligence: type info, cross-references, diagnostics, refactoring.

1. Read TECHSTACK.md to identify detected languages
2. If languages detected that have LSP support (TypeScript/JS, Python, Go, Rust, Java, C#, Kotlin):
   a. Prompt user: "Install LSP servers for [detected languages]? This improves AI code quality. (recommended) [Y/n]"
   b. If user accepts:
      - ACQUIRE `lsp-install/SKILL.md` FROM KB
      - Execute skill with detected languages
      - Report results: installed, skipped, failed
   c. If user declines: log as "LSP installation skipped by user choice"
3. Update state with LSP status (installed/skipped/not-applicable)

</lsp_prompt>

<pitfalls>

- Do not re-ask questions answered as in-phase blockers — check state
- Unanswered questions: log as deferred gap, do not guess

</pitfalls>

</init_workspace_flow_questions>
