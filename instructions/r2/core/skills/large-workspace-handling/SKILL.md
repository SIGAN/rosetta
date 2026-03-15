---
name: large-workspace-handling
description: "Rosetta skill to partition large workspaces or folders (50+ files recursively) into scoped subagent tasks when single-agent context is insufficient."
tags: ["skill", "workspace", "large-workspace", "delegation"]
baseSchema: docs/schemas/skill.md
---

<large_workspace_handling>

<role>

Workspace partitioning strategist. Draws scope boundaries, dispatches subagents.

</role>

<when_to_use_skill>
Use when large workspaces exceed single-agent context window. Partitions into write-scopes where every file belongs to exactly one scope, and merged results address the original request completely.
</when_to_use_skill>

<core_concepts>

- Rosetta prep steps completed
- If `CODEMAP.md` missing, ACQUIRE `init-workspace-discovery/SKILL.md` FROM KB and EXECUTE to create ONLY it
- Grep `#` headers of CODEMAP before scoping

Summarize mode:
- Assign subagents: scope paths, goal, output format and level of detail
- Subagents ACQUIRE `reverse-engineering/SKILL.md` FROM KB for code analysis
- Summarize all outputs

Change mode:
- Divide change scope across subagents: scope paths, goal, read-only deps, output expectations
- Subagents decide and execute changes within declared scope
- Resolve cross-scope deps via execution ordering
- Resolve shared-interface conflicts or changes with extra pass
- Produce unified result

Scoping:
- Partition into independent areas
- One subagent per area or logical group
- Group coupled paths into one scope
- Align to monorepo boundaries when present

</core_concepts>

</large_workspace_handling>
