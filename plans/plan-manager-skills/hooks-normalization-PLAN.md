# Plan: Hook Input Normalization + Loose Files Hook

## Context

**Epic:** Rosetta v3 Determinism (CTORNDGAIN-1286)
**Why:** AI coding agents (Claude Code, Codex, Cursor, etc.) each pass slightly different JSON schemas to hooks. Every Rosetta hook would need to handle all formats independently — O(hooks x tools) complexity. A single normalization adapter reduces this to O(hooks + tools), and all subsequent hooks just consume the normalized model.
**Second task:** `.py`/`.js` files created outside proper modules is a common AI coding agent mistake. A lightweight nudge hook catches this early.
**Dependency:** PR #48 (rosettify/plan_manager) — MERGED. No blockers.

## Scope

| In scope | Out of scope |
|----------|-------------|
| `adapter.js` — normalization library | Hook delivery mechanism (init-workspace-flow) |
| `adapter.test.js` — unit tests | Testing on IDEs other than Claude Code (follow-up) |
| `loose-files.js` — PostToolUse hook | Scoped npm package for rosettify |
| `loose-files.test.js` — unit tests | Fixing exploratory-test-feedback items |
| Claude Code hook config example | Other hooks (doc/md, debug leftovers, shell scripts) |
| pre_commit.py update to sync hooks | |

## Task 1: Common Hook Input Normalization (3 SP)

### File: `instructions/r2/core/hooks/adapter.js`

**Purpose:** Single JS module that normalizes hook stdin JSON from any IDE into Claude Code canonical format, and normalizes output back to IDE-specific format.

**Canonical (Claude Code) input fields we need:**

```json
{
  "session_id": "string",
  "transcript_path": "string",
  "cwd": "string",
  "permission_mode": "string",          // default|plan|acceptEdits|auto|bypassPermissions
  "hook_event_name": "string",          // PostToolUse, PreToolUse, etc.
  "tool_name": "string",                // Write, Edit, Bash, etc.
  "tool_use_id": "string",              // unique ID for this tool invocation
  "agent_id": "string",                 // optional: only in subagent contexts
  "agent_type": "string",               // optional: only in subagent contexts
  "tool_input": {
    "file_path": "string",              // primary field for Write/Edit hooks
    "command": "string",                // for Bash hooks
    "content": "string"                 // for Write hooks
  },
  "tool_response": "object"             // PostToolUse only
}
```

**Exported functions:**

| Function | Purpose |
|----------|---------|
| `readStdin()` | Read stdin, parse JSON, return Promise<object> |
| `normalize(rawInput)` | Detect IDE from input shape, normalize to canonical format |
| `formatOutput(canonicalOutput, ide)` | Convert canonical output JSON to IDE-specific format |
| `detectIDE(rawInput)` | Heuristic: detect which IDE from input field names |

**IDE detection strategy:**
- Claude Code: has `hook_event_name`, `tool_input`, `session_id`
- Cursor: has `args`, `command` at top level (from reference adapter.js)
- Codex/others: TBD — dump raw input first, then add detection

**Implementation steps:**

1. Create `instructions/r2/core/hooks/adapter.js` with `readStdin()` + `normalize()` + `formatOutput()` + `detectIDE()`
2. Claude Code path = identity (it's the canonical format, just pass through)
3. Cursor path = transform based on reference adapter.js field mapping
4. Other IDEs = stub with `throw new Error('Unsupported IDE: ...')` for now
5. Create `instructions/r2/core/hooks/adapter.test.js` with:
   - Unit tests with fixture JSON for Claude Code input
   - Unit tests with fixture JSON for Cursor input
   - Test that unknown IDE throws clear error
   - Test readStdin with mock stdin
6. Manual e2e test: install hook in a real Claude Code project, trigger file edit, verify normalized output

### Testing approach (from Igor):
- Create a simple hook that dumps raw stdin to a file
- Run same prompt in Claude Code → capture input JSON
- Later: repeat for Cursor, Codex, VS Code → capture their input JSONs
- Use captured JSONs as test fixtures

## Task 2: Hook for *.py, *.js Outside Modules (1 SP)

### File: `instructions/r2/core/hooks/loose-files.js`

**Purpose:** PostToolUse hook that checks if newly created/edited `.py` or `.js` files are outside proper module boundaries. Outputs a nudge message for the AI to reconsider.

**Logic:**

```
1. Read stdin via adapter.readStdin() + adapter.normalize()
2. Filter: only PostToolUse events for Write or Edit tools
3. Extract file_path from normalized input
4. Check extension: .py or .js only
5. Exclusions: skip if path contains agents/TEMP/, scripts/, node_modules/, .venv/
6. For .py: walk up directories looking for __init__.py → if not found = loose file
7. For .js: walk up directories looking for package.json → if not found = loose file
8. If loose: output nudge message via stdout JSON
9. If not loose: exit 0 silently (no output)
```

**Nudge message (stdout JSON):**

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "File <path> was created outside of a recognized <Python|JavaScript> module (no <__init__.py|package.json> found in parent directories). Consider whether this file should be placed inside an existing module, or if a new module structure is needed."
  },
  "continue": true,
  "suppressOutput": false
}
```

**Implementation steps:**

1. Create `instructions/r2/core/hooks/loose-files.js` using adapter.js
2. Create `instructions/r2/core/hooks/loose-files.test.js`:
   - Mock filesystem with `__init__.py` present → no output
   - Mock filesystem without `__init__.py` → nudge output
   - Same for `package.json` / `.js`
   - Exclusion paths (agents/TEMP/) → no output
   - Non-.py/.js files → no output
3. Manual e2e: configure hook in Claude Code, ask AI to create a loose `.py` file, verify nudge appears

## Supporting Changes

### Update `scripts/pre_commit.py`

Add `hooks/` to the sync list so `instructions/r2/core/hooks/` → `plugins/core-claude/hooks/` (same as skills, agents, etc.)

### Hook config example

Provide example `settings.json` snippet for users:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/loose-files.js\""
          }
        ]
      }
    ]
  }
}
```

## File Summary

| File | Action | Purpose |
|------|--------|---------|
| `instructions/r2/core/hooks/adapter.js` | CREATE | Input/output normalization |
| `instructions/r2/core/hooks/adapter.test.js` | CREATE | Unit tests for adapter |
| `instructions/r2/core/hooks/loose-files.js` | CREATE | Loose file detection hook |
| `instructions/r2/core/hooks/loose-files.test.js` | CREATE | Unit tests for loose-files |
| `scripts/pre_commit.py` | EDIT | Add hooks/ to sync targets |

## Execution Order

```
Phase 1: adapter.js + tests          ← Task 1 core
Phase 2: e2e test on Claude Code     ← Task 1 validation
Phase 3: loose-files.js + tests      ← Task 2 core
Phase 4: e2e test on Claude Code     ← Task 2 validation
Phase 5: pre_commit.py update        ← Supporting change
```

## Verification

1. `node adapter.test.js` — all unit tests pass
2. `node loose-files.test.js` — all unit tests pass
3. Manual: install hooks in a Claude Code project, create a `.py` file outside any module → verify nudge message appears in AI context
4. Manual: create a `.py` file inside a module with `__init__.py` → verify no nudge
5. `venv/bin/python scripts/pre_commit.py` — hooks synced to plugins/core-claude/hooks/
6. Verify `plugins/core-claude/hooks/adapter.js` exists after pre_commit sync

## Risks

| Risk | Mitigation |
|------|-----------|
| Claude Code hook schema may differ from docs | Dump raw stdin first, use as fixture |
| `fs.existsSync` walk-up may be slow on deep trees | Cap at 10 levels or stop at `.git` |
| Other hooks team members write may need different normalized fields | Keep adapter minimal, add fields as needed |
