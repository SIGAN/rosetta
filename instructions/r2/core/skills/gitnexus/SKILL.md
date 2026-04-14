---
name: gitnexus
description: "Opt-in skill: install and use GitNexus for semantic code-graph navigation in Claude Code. Provides caller discovery, impact analysis, and refactoring safety via MCP tools."
tags: ["gitnexus", "code-graph", "navigation", "impact-analysis", "refactoring", "opt-in"]
baseSchema: docs/schemas/skill.md
---

<gitnexus>

<role>
Code-graph navigator — uses GitNexus MCP tools to find callers, assess blast radius, and navigate large codebases accurately instead of grepping.
</role>

<when_to_use_skill>
Use when the codebase is already indexed by GitNexus (`.gitnexus/` directory exists) and you need to:
- Find all callers of a function or method across the repo
- Assess the blast radius before modifying a symbol
- Rename or refactor safely without missing call sites
- Understand how an execution flow is wired together

Do NOT activate this skill if `.gitnexus/` is absent — GitNexus has not been installed for this repo.
</when_to_use_skill>

<installation>

**Prerequisites:** Node.js 18+, npm.

**Step 1 — Install GitNexus CLI globally:**
```bash
npm install -g gitnexus
```

**Step 2 — Index the repository (run once, then after major refactors):**
```bash
cd /path/to/repo
npx gitnexus analyze
```

Index time: ~5 min for a medium repo (~4k symbols). Output stored in `.gitnexus/`.
Add `.gitnexus` to `.gitignore` — the index is local and not committed.

**Step 3 — Register as a Claude Code MCP server:**

Option A — `gitnexus setup` (automatic):
```bash
npx gitnexus setup
```
Registers the stdio MCP in `~/.claude.json` and installs the default hook.

Option B — Manual (project-scoped, recommended for teams):
Add to `.mcp.json` in the repo root:
```json
{
  "mcpServers": {
    "gitnexus": {
      "type": "stdio",
      "command": "gitnexus",
      "args": ["mcp"]
    }
  }
}
```

**Step 4 — Enable the silent re-index hook (opt-in):**

Add to `.claude/settings.json` or `~/.claude.json`:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "node /path/to/rosetta/scripts/hooks/gitnexus-refresh.cjs"
      }]
    }]
  }
}
```

This triggers `gitnexus analyze` silently in the background after every file edit, with a 5-second debounce. The agent never sees the output.

**Step 5 — Verify:**
```
/mcp
```
GitNexus should appear as `gitnexus · ✔ connected`.

</installation>

<tools>

| Tool | When to use |
|------|-------------|
| `gitnexus_impact({target, direction:"upstream"})` | **Primary caller discovery.** Use before any modification. Returns cross-repo blast radius. |
| `gitnexus_context({name})` | Full 360° view of one symbol: callers, callees, execution flows. |
| `gitnexus_query({query})` | Find code by concept when you don't know the exact symbol name. |
| `gitnexus_detect_changes()` | Pre-commit scope check — confirms only expected symbols changed. |
| `gitnexus_rename({symbol_name, new_name, dry_run:true})` | Safe multi-file rename via call graph. Always dry-run first. |

**Key rule:** Always run `gitnexus_impact` with `direction:"upstream"` to find cross-module callers. `gitnexus_context` is local-scope only and misses callers in other packages.

</tools>

<process>

1. Before modifying any symbol:
   - Run `gitnexus_impact({target: "symbolName", direction: "upstream"})`
   - Report blast radius to user (direct callers at d=1, indirect at d=2/3)
   - If risk is HIGH or CRITICAL, warn the user before proceeding

2. During navigation:
   - Prefer `gitnexus_impact` over Grep for caller discovery
   - Use `gitnexus_context` for local symbol details (callers within the same file/module)
   - Use `gitnexus_query` for concept-based exploration

3. After editing:
   - Run `gitnexus_detect_changes()` to verify scope matches expectations
   - If the re-index hook is not installed, remind the user to run `npx gitnexus analyze` before the next session

4. For renames:
   - Always use `gitnexus_rename` with `dry_run: true` first
   - Review the preview before applying
   - Never use find-and-replace for symbol renames

</process>

<index_staleness>

The GitNexus index becomes stale the moment files are edited. Two ways to keep it fresh:

**Automatic (recommended):** Install the re-index hook (`scripts/hooks/gitnexus-refresh.cjs`). It fires silently after every Edit/Write/MultiEdit with a 5-second debounce.

**Manual:** Run `npx gitnexus analyze` at the start of each session or after a batch of edits.

If embeddings were generated during the initial index, preserve them:
```bash
npx gitnexus analyze --embeddings
```

Check `.gitnexus/meta.json` → `stats.embeddings` to see if embeddings exist (0 means none).

</index_staleness>

<known_limitations>

- **Extensions:** `vector` and `fts` extensions download from a third-party CDN at index time. They may fail on restricted corporate networks. Core graph navigation still works without them.
- **Index time:** Full re-index of a large repo (~4k symbols) takes ~5 min. The async hook debounces to avoid thrashing on multi-file edits.
- **MCP scope:** `gitnexus_context` returns intra-module callers only. Always use `gitnexus_impact` for cross-repo caller discovery.

</known_limitations>

</gitnexus>
