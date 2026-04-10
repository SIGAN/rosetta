#!/usr/bin/env bash
# capture-hook-fixtures.sh — E2E hook stdin capture for Claude Code and Codex CLI
#
# Spins up a temp project, installs dump-stdin.js as a hook for each IDE,
# triggers a hook event, extracts the captured JSON, and saves sanitized
# fixtures to test-fixtures/.
#
# Usage:
#   ./capture-hook-fixtures.sh                  # capture both IDEs
#   ./capture-hook-fixtures.sh --ide claude-code
#   ./capture-hook-fixtures.sh --ide codex
#   ./capture-hook-fixtures.sh --dry-run        # show commands, no execution
#
# Requirements: node, python3, claude (CLI), codex (CLI)

set -Eeuo pipefail

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
FIXTURES_DIR="$SCRIPT_DIR/test-fixtures"
DUMP_SCRIPT="$FIXTURES_DIR/dump-stdin.js"
DUMP_FILE="/tmp/hook-stdin-dump.jsonl"
TEST_DIR="/tmp/hook-e2e-test"

# ── Colours ───────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
  GRN='\033[0;32m' YLW='\033[0;33m' RED='\033[0;31m' BLU='\033[0;34m' RST='\033[0m'
else
  GRN='' YLW='' RED='' BLU='' RST=''
fi

log_info()  { echo -e "${BLU}[INFO]${RST}  $*"; }
log_ok()    { echo -e "${GRN}[ OK ]${RST}  $*"; }
log_warn()  { echo -e "${YLW}[WARN]${RST}  $*"; }
log_error() { echo -e "${RED}[ERR ]${RST}  $*" >&2; }

# ── Argument parsing ──────────────────────────────────────────────────────────
DRY_RUN=false
TARGET_IDE="both"   # both | claude-code | codex

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    DRY_RUN=true; shift ;;
    --ide)        TARGET_IDE="$2"; shift 2 ;;
    --ide=*)      TARGET_IDE="${1#*=}"; shift ;;
    -h|--help)
      sed -n '/^# Usage:/,/^$/p' "$0"
      exit 0 ;;
    *) log_error "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ "$TARGET_IDE" != "both" && "$TARGET_IDE" != "claude-code" && "$TARGET_IDE" != "codex" ]]; then
  log_error "--ide must be 'both', 'claude-code', or 'codex'"
  exit 1
fi

# ── Dry-run wrapper ───────────────────────────────────────────────────────────
run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YLW}[DRY-RUN]${RST} $*"
    return 0
  fi
  "$@"
}

# ── Dependency check ──────────────────────────────────────────────────────────
check_deps() {
  local missing=()
  command -v node    &>/dev/null || missing+=("node")
  command -v python3 &>/dev/null || missing+=("python3")

  [[ "$TARGET_IDE" == "both" || "$TARGET_IDE" == "claude-code" ]] \
    && command -v claude &>/dev/null || { [[ "$TARGET_IDE" == "claude-code" || "$TARGET_IDE" == "both" ]] && missing+=("claude"); }

  # Codex: prefer npx @openai/codex (>=0.118, has hooks) over brew codex (0.39, no hooks)
  if [[ "$TARGET_IDE" == "both" || "$TARGET_IDE" == "codex" ]]; then
    if ! npx --yes @openai/codex --version &>/dev/null; then
      missing+=("@openai/codex (npx)")
    fi
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    log_error "Missing required commands: ${missing[*]}"
    exit 1
  fi
  local codex_ver
  codex_ver=$(npx @openai/codex --version 2>/dev/null || echo "n/a")
  log_ok "Dependencies: node, python3$(command -v claude &>/dev/null && echo ", claude")$(  [[ "$TARGET_IDE" == "both" || "$TARGET_IDE" == "codex" ]] && echo ", codex ($codex_ver via npx)")"
}

# ── Setup temp project ────────────────────────────────────────────────────────
setup_test_project() {
  log_info "Setting up test project at $TEST_DIR"
  run rm -f "$DUMP_FILE"
  run mkdir -p "$TEST_DIR/.claude" "$TEST_DIR/.codex"
  run bash -c "cd '$TEST_DIR' && git init -q 2>/dev/null || true"
  run bash -c "echo \"print('hello')\" > '$TEST_DIR/existing.py'"

  # Claude Code hook config
  run bash -c "cat > '$TEST_DIR/.claude/settings.json' << 'SETTINGS_EOF'
{
  \"hooks\": {
    \"PostToolUse\": [
      {
        \"matcher\": \"Write|Edit\",
        \"hooks\": [{ \"type\": \"command\", \"command\": \"node $DUMP_SCRIPT\" }]
      }
    ],
    \"PreToolUse\": [
      {
        \"matcher\": \"Bash\",
        \"hooks\": [{ \"type\": \"command\", \"command\": \"node $DUMP_SCRIPT\" }]
      }
    ]
  }
}
SETTINGS_EOF"

  # Codex hook config — same structure, Bash-only (Codex v0.39 only hooks Bash)
  run bash -c "cat > '$TEST_DIR/.codex/hooks.json' << 'CODEX_EOF'
{
  \"hooks\": {
    \"PostToolUse\": [
      {
        \"matcher\": \"Bash\",
        \"hooks\": [{ \"type\": \"command\", \"command\": \"node $DUMP_SCRIPT\" }]
      }
    ],
    \"PreToolUse\": [
      {
        \"matcher\": \"Bash\",
        \"hooks\": [{ \"type\": \"command\", \"command\": \"node $DUMP_SCRIPT\" }]
      }
    ]
  }
}
CODEX_EOF"

  log_ok "Test project ready"
}

# ── Sanitize captured JSON ────────────────────────────────────────────────────
# Replaces real paths and session IDs with generic placeholders.
sanitize_fixture() {
  python3 - "$1" << 'PY'
import sys, json, re, os

with open(sys.argv[1]) as f:
    data = json.load(f)

def sanitize(val, key=""):
    if not isinstance(val, str):
        return val
    # Replace real home paths
    val = re.sub(r'/Users/[^/]+', '/Users/dev', val)
    val = re.sub(r'/home/[^/]+', '/home/dev', val)
    # Replace session/turn IDs and tool use IDs
    if key in ('session_id', 'tool_use_id', 'turn_id'):
        val = re.sub(r'.+', f'sanitized-{key}', val)
    # Sanitize UUIDs anywhere (e.g. in transcript_path)
    val = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', val)
    return val

def walk(obj, parent_key=""):
    if isinstance(obj, dict):
        return {k: walk(v, k) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [walk(i) for i in obj]
    elif isinstance(obj, str):
        return sanitize(obj, parent_key)
    return obj

print(json.dumps(walk(data), indent=2))
PY
}

# ── Extract fixture for a given IDE from the dump ─────────────────────────────
# Prints the last matching JSON object from the dump file.
extract_fixture() {
  local ide="$1"   # "claude-code" or "codex"
  python3 - "$DUMP_FILE" "$ide" << 'PY'
import sys, json

dump_file = sys.argv[1]
ide = sys.argv[2]

matches = []
with open(dump_file) as f:
    for line in f:
        entry = json.loads(line.strip())
        inp = entry.get("input") or {}
        has_model_turn = "model" in inp and "turn_id" in inp
        is_codex = ide == "codex" and has_model_turn
        is_cc    = ide == "claude-code" and not has_model_turn and "hook_event_name" in inp
        if is_codex or is_cc:
            matches.append(inp)

if not matches:
    print(f"NO_MATCH", file=sys.stderr)
    sys.exit(1)

print(json.dumps(matches[-1], indent=2))
PY
}

# ── Capture: Claude Code ──────────────────────────────────────────────────────
capture_claude_code() {
  log_info "Capturing Claude Code hook stdin..."
  local tmp_fixture=""
  if [[ "$DRY_RUN" == "false" ]]; then
    tmp_fixture="$(mktemp)"
    trap 'rm -f "${tmp_fixture:-}"' RETURN
  fi

  local prompt="Create a file called cc_capture.py with exactly: def hello(): return 'hello'"

  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would run: cd $TEST_DIR && claude -p \"$prompt\""
    return 0
  fi

  (cd "$TEST_DIR" && claude -p "$prompt" --output-format text 2>&1) \
    || { log_warn "claude exited non-zero — checking dump anyway"; }

  if [[ ! -f "$DUMP_FILE" ]]; then
    log_error "No dump captured — hook may not have fired"
    return 1
  fi

  if ! extract_fixture "claude-code" > "$tmp_fixture" 2>/dev/null; then
    log_warn "No Claude Code entry found in dump (hook may not have fired for Write)"
    log_warn "Dump contents:"
    cat "$DUMP_FILE" | python3 -m json.tool 2>/dev/null || cat "$DUMP_FILE"
    return 1
  fi

  local out="$FIXTURES_DIR/claude-code-post-tool-use-write.json"
  sanitize_fixture "$tmp_fixture" > "$out"
  log_ok "Saved: $out"
}

# ── Capture: Codex CLI ────────────────────────────────────────────────────────
capture_codex() {
  log_info "Capturing Codex CLI hook stdin..."
  local tmp_fixture=""
  if [[ "$DRY_RUN" == "false" ]]; then
    tmp_fixture="$(mktemp)"
    trap 'rm -f "${tmp_fixture:-}"' RETURN
  fi

  # Reset dump so we get only Codex entries
  run rm -f "$DUMP_FILE"

  local prompt="Run exactly: echo codex_hook_test > /tmp/codex_hook_test.txt && echo done"

  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would run: cd $TEST_DIR && npx @openai/codex exec --full-auto \"$prompt\""
    return 0
  fi

  local exit_code=0
  (cd "$TEST_DIR" && npx @openai/codex exec --full-auto "$prompt" 2>&1) || exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    log_warn "npx codex exec exited with code $exit_code (may be auth issue) — checking dump"
  fi

  if [[ ! -f "$DUMP_FILE" ]]; then
    log_error "No dump captured. Possible causes:"
    log_error "  1. Codex auth expired — run: npx @openai/codex login"
    log_error "  2. Hooks not firing — check .codex/hooks.json is in project root"
    log_error "  3. codex_hooks feature not enabled — add [features] codex_hooks=true to ~/.codex/config.toml"
    return 1
  fi

  if ! extract_fixture "codex" > "$tmp_fixture" 2>/dev/null; then
    log_warn "No Codex entry in dump. Dump contents:"
    cat "$DUMP_FILE" | python3 -m json.tool 2>/dev/null || cat "$DUMP_FILE"
    return 1
  fi

  local out="$FIXTURES_DIR/codex-post-tool-use-bash.json"
  sanitize_fixture "$tmp_fixture" > "$out"

  # Strip the schema-derived _note if present from previous fixture
  python3 -c "
import json, sys
with open('$out') as f: d = json.load(f)
d.pop('_note', None)
print(json.dumps(d, indent=2))
" > "${out}.tmp" && mv "${out}.tmp" "$out"

  log_ok "Saved: $out"
}

# ── Run tests ─────────────────────────────────────────────────────────────────
run_tests() {
  log_info "Running adapter tests..."
  if node --test "$SCRIPT_DIR/adapter.test.js" 2>&1 \
      | grep -E "^# (pass|fail|todo)" | head -5; then
    log_ok "adapter.test.js passed"
  else
    log_error "adapter.test.js failed — check output above"
    return 1
  fi

  log_info "Running loose-files tests..."
  if node --test "$SCRIPT_DIR/loose-files.test.js" 2>&1 \
      | grep -E "^# (pass|fail|todo)" | head -5; then
    log_ok "loose-files.test.js passed"
  else
    log_error "loose-files.test.js failed"
    return 1
  fi
}

# ── Print captured fixture summary ───────────────────────────────────────────
print_summary() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Fixture capture summary"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  for f in \
    "$FIXTURES_DIR/claude-code-post-tool-use-write.json" \
    "$FIXTURES_DIR/codex-post-tool-use-bash.json"; do
    if [[ -f "$f" ]]; then
      local ide_field model_field turn_field
      ide_field=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('hook_event_name','?'))" 2>/dev/null || echo "?")
      model_field=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('model','—'))" 2>/dev/null || echo "—")
      turn_field=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('turn_id','—'))" 2>/dev/null || echo "—")
      echo -e "  ${GRN}✓${RST} $(basename "$f")"
      echo "      hook_event_name: $ide_field | model: $model_field | turn_id: $turn_field"
    else
      echo -e "  ${YLW}–${RST} $(basename "$f")  (not captured)"
    fi
  done
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Hook fixture capture   (IDE: $TARGET_IDE)"
  [[ "$DRY_RUN" == "true" ]] && echo "  MODE: DRY RUN"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  check_deps
  setup_test_project

  local captured_any=false

  if [[ "$TARGET_IDE" == "both" || "$TARGET_IDE" == "claude-code" ]]; then
    if capture_claude_code; then
      captured_any=true
    else
      log_warn "Claude Code capture failed — continuing"
    fi
  fi

  if [[ "$TARGET_IDE" == "both" || "$TARGET_IDE" == "codex" ]]; then
    if capture_codex; then
      captured_any=true
    else
      log_warn "Codex capture failed — continuing"
    fi
  fi

  print_summary

  if [[ "$captured_any" == "true" && "$DRY_RUN" == "false" ]]; then
    run_tests
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    log_info "Dry-run complete — no files written"
  elif [[ "$captured_any" == "true" ]]; then
    log_ok "Done. Review fixtures in $FIXTURES_DIR, then commit."
  else
    log_warn "No fixtures captured. Check errors above."
    exit 1
  fi
}

main
