#!/bin/bash
find /tmp -maxdepth 1 -name "rosetta-bootstrap-*.lock" -mmin +1 -delete 2>/dev/null
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')
LOCK="/tmp/rosetta-bootstrap-${SESSION_ID}.lock"
if [ -f "$LOCK" ]; then exit 0; fi
touch "$LOCK"
PLUGIN_ROOT="$(cd "$(dirname "$0")" && pwd)"
cat "$PLUGIN_ROOT/rules/bootstrap-core-policy.md" \
    "$PLUGIN_ROOT/rules/bootstrap-execution-policy.md" \
    "$PLUGIN_ROOT/rules/bootstrap-guardrails.md" \
    "$PLUGIN_ROOT/rules/bootstrap-hitl-questioning.md" \
    "$PLUGIN_ROOT/rules/bootstrap-rosetta-files.md" \
    "$PLUGIN_ROOT/rules/plugin-files-mode.md" \
    "$PLUGIN_ROOT/rules/INDEX.md" \
    "$PLUGIN_ROOT/workflows/INDEX.md"
echo ""
echo "Rosetta Core Plugin Path: $PLUGIN_ROOT"
