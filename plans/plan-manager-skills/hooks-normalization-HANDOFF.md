# Handoff: Hook Input Normalization + Loose Files Hook

**Branch:** `feature/hooks-normalization-tdd`
**Date:** 2026-04-07
**Epic:** Rosetta v3 Determinism (CTORNDGAIN-1286)
**Source plan:** `plans/plan-manager-skills/hooks-normalization-PLAN.md`

---

## What Was Done This Session

### ✅ Phase 0 — Plan schema patched

`plans/plan-manager-skills/hooks-normalization-PLAN.md` updated:
- Canonical Claude Code input now includes: `permission_mode`, `tool_use_id`, `agent_id`, `agent_type`
- Output schema updated: added `continue`, `stopReason`, `suppressOutput`, `systemMessage`

### ✅ Phase 1 — All test fixtures created

`instructions/r2/core/hooks/test-fixtures/`:

| File | Status | Notes |
|------|--------|-------|
| `claude-code-post-tool-use-write.json` | ✅ Real schema | PostToolUse + Write, all 11 fields |
| `claude-code-post-tool-use-edit.json` | ✅ Real schema | PostToolUse + Edit |
| `claude-code-pre-tool-use-bash.json` | ✅ Real schema | PreToolUse + Bash, no tool_response |
| `claude-code-post-tool-use-write-subagent.json` | ✅ Real schema | Has agent_id + agent_type |
| `cursor-post-tool-use-write.json` | 🔴 Stub | `{ "TODO": true, "_ide": "cursor" }` |
| `codex-post-tool-use-write.json` | 🔴 Stub | `{ "TODO": true, "_ide": "codex" }` |
| `windsurf-post-tool-use-write.json` | 🔴 Stub | `{ "TODO": true, "_ide": "windsurf" }` |
| `copilot-post-tool-use-write.json` | 🔴 Stub | `{ "TODO": true, "_ide": "copilot" }` |
| `unknown-ide-input.json` | ✅ Done | Random shape for error path |
| `dump-stdin.js` | ✅ Done | Helper to capture real IDE stdin |

### ✅ Phase 2 — TDD test suites written (currently RED)

`instructions/r2/core/hooks/adapter.test.js` — confirmed RED:
```
Error: Cannot find module './adapter'
```

`instructions/r2/core/hooks/loose-files.test.js` — confirmed RED:
```
Error: Cannot find module './loose-files'
```

Run to verify RED:
```bash
node --test instructions/r2/core/hooks/adapter.test.js
node --test instructions/r2/core/hooks/loose-files.test.js
```

---

## What Remains (Next Session)

### Step 4: Implement `adapter.js` → GREEN

**File to create:** `instructions/r2/core/hooks/adapter.js`

**Must export:**
```js
module.exports = { readStdin, normalize, formatOutput, detectIDE };
```

**Function contracts:**

```js
// Detect which IDE sent the input based on field shape heuristics
function detectIDE(rawInput)
// Claude Code: has hook_event_name + tool_input + session_id
// Cursor: TBD (stub returns throw for now)
// Unknown: throw new Error(`Unsupported IDE: ${JSON.stringify(Object.keys(rawInput))}`)

// Normalize any IDE input to Claude Code canonical format
function normalize(rawInput)
// Claude Code: identity pass-through (already canonical)
// Other IDEs: field mapping (TBD when real fixtures available)

// Convert canonical output to IDE-specific output format
function formatOutput(canonicalOutput, ide)
// Claude Code: identity pass-through
// Other IDEs: TBD

// Read and parse JSON from stdin (or injected stream for testing)
async function readStdin(stream = process.stdin)
// Throws on empty or invalid JSON
```

**Expected test results after Step 4:**
```
adapter.test.js:
  ✅ ~13 GREEN  — Claude Code paths + error paths
  🔴  12 TODO   — Stub IDE tests (marked with { todo: '...' }, expected to skip/fail)
```

### Step 5: Implement `loose-files.js` → GREEN

**File to create:** `instructions/r2/core/hooks/loose-files.js`

**Must export (for testability):**
```js
module.exports = { shouldCheck, isLooseFile, buildNudgeOutput };
```

**Function contracts:**

```js
// Returns true if this hook should process this normalized input
function shouldCheck(normalizedInput)
// true when: hook_event_name === 'PostToolUse'
//            AND tool_name in ['Write', 'Edit']
//            AND extension in ['.py', '.js']
//            AND file_path does NOT contain excluded dirs:
//               agents/TEMP/, scripts/, node_modules/, .venv/, __pycache__/

// Walk up directories looking for module marker file
// .py → __init__.py, .js → package.json
// Stops at .git directory OR after 10 levels
// fs param is injectable for testing (default: require('fs'))
function isLooseFile(filePath, fs = require('fs'))

// Build the nudge JSON output for stdout
function buildNudgeOutput(filePath)
// Returns: { hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: '...' }, continue: true, suppressOutput: false }

// Main entrypoint when run as hook (reads stdin via adapter, writes to stdout)
// Only when require.main === module
if (require.main === module) { ... }
```

**Expected test results after Step 5:**
```
loose-files.test.js:
  ✅ ~28 GREEN — all tests pass
```

### Step 6: Update `scripts/pre_commit.py`

Add `hooks/` to the sync targets. Exclude `test-fixtures/` and `*.test.js` from sync to `plugins/core-claude/hooks/`.

Look at `copy_core_tree()` in `scripts/pre_commit.py` — the sync logic iterates `instructions/r2/core/`. Add filter to exclude test files when copying hooks.

### Step 7: Regression

```bash
venv/bin/pytest ims-mcp-server/tests
venv/bin/pytest rosetta-cli/tests
./validate-types.sh
venv/bin/python scripts/pre_commit.py
```

Verify: `plugins/core-claude/hooks/adapter.js` and `loose-files.js` exist. Test files do NOT sync.

### Step 8: Manual E2E

See `plans/plan-manager-skills/hooks-normalization-PLAN.md` → Verification section.

Key scenario: configure `dump-stdin.js` as a hook, trigger Write, capture real stdin to `/tmp/hook-stdin-dump.jsonl`, compare against fixture. Update fixture if fields differ.

---

## Architecture Decisions Made

| Decision | Choice | Reason |
|----------|--------|--------|
| Test framework | `node:test` + `node:assert` (built-in) | Zero deps, no package.json needed |
| Module format | CJS (`require`) | Widest IDE compatibility |
| Stub IDE tests | `{ todo: '...' }` in node:test | Tests are wired up, skip until real fixtures |
| Dependency injection | `isLooseFile(path, fs)` | Testable without touching real filesystem |
| Test files in plugins | NO — excluded from sync | Tests are dev artifacts, not delivery |

---

## File Structure

```
instructions/r2/core/hooks/
├── adapter.js                    ← NEXT: implement (Step 4)
├── adapter.test.js               ✅ written, 🔴 RED
├── loose-files.js                ← NEXT: implement (Step 5)
├── loose-files.test.js           ✅ written, 🔴 RED
└── test-fixtures/
    ├── dump-stdin.js             ✅ helper
    ├── claude-code-*.json        ✅ real fixtures (4 files)
    ├── cursor-*.json             🔴 stub
    ├── codex-*.json              🔴 stub
    ├── windsurf-*.json           🔴 stub
    ├── copilot-*.json            🔴 stub
    └── unknown-ide-input.json    ✅ error path fixture
```

---

## Quick Start for New Session

```bash
# 1. Switch to branch
git checkout feature/hooks-normalization-tdd

# 2. Confirm RED state
node --test instructions/r2/core/hooks/adapter.test.js
node --test instructions/r2/core/hooks/loose-files.test.js

# 3. Read source plan
cat plans/plan-manager-skills/hooks-normalization-PLAN.md

# 4. Implement adapter.js (Step 4)
# 5. Implement loose-files.js (Step 5)
# 6. Update scripts/pre_commit.py (Step 6)
# 7. Run regression (Step 7)
```
