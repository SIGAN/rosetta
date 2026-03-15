#!/bin/bash

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Rosetta Type Validation ===${NC}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/mypy.ini"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}ERROR: mypy config not found: $CONFIG_FILE${NC}"
    exit 1
fi

if command -v uvx >/dev/null 2>&1; then
    TYPECHECK_CMD=(uvx mypy)
elif python3 -m mypy --version >/dev/null 2>&1; then
    TYPECHECK_CMD=(python3 -m mypy)
elif command -v mypy >/dev/null 2>&1; then
    TYPECHECK_CMD=(mypy)
else
    echo -e "${RED}ERROR: No mypy runner found. Install uv or mypy before running type validation.${NC}"
    exit 1
fi

echo -e "${BLUE}Running type validation...${NC}"
"${TYPECHECK_CMD[@]}" --config-file "$CONFIG_FILE"

echo -e "${GREEN}Type validation passed${NC}"
