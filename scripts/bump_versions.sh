#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Cross-platform sed in-place
if [[ "$OSTYPE" == "darwin"* ]]; then
    sedi() { sed -i '' "$@"; }
else
    sedi() { sed -i "$@"; }
fi

get_toml_version() {
    grep '^version = ' "$1" | head -1 | sed 's/version = "\(.*\)"/\1/'
}

get_json_version() {
    grep '"version"' "$1" | head -1 | sed 's/.*"version": "\(.*\)".*/\1/'
}

bump_semver() {
    local version="$1" type="$2"
    IFS='.' read -r major minor patch <<< "$version"
    case "$type" in
        major) echo "$((major + 1)).0.0" ;;
        minor) echo "${major}.$((minor + 1)).0" ;;
        patch) echo "${major}.${minor}.$((patch + 1))" ;;
    esac
}

ask_yn() {
    local prompt="$1" default="$2" answer
    if [[ "$default" == "y" ]]; then
        read -r -p "  $prompt [Y/n]: " answer
        answer="${answer:-y}"
    else
        read -r -p "  $prompt [y/N]: " answer
        answer="${answer:-n}"
    fi
    [[ "$answer" =~ ^[Yy]$ ]]
}

TOML_FILES=(
    "$ROOT/rosetta-cli/pyproject.toml"
    "$ROOT/ims-mcp-server/pyproject.toml"
    "$ROOT/rosetta-mcp-server/pyproject.toml"
)

PLUGIN_FILES=(
    "$ROOT/plugins/rosetta/.claude-plugin/plugin.json"
    "$ROOT/plugins/rosetta/.cursor-plugin/plugin.json"
    "$ROOT/instructions/r2/core/.claude-plugin/plugin.json"
    "$ROOT/instructions/r2/core/.cursor-plugin/plugin.json"
)

MARKETPLACE_FILES=(
    "$ROOT/.claude-plugin/marketplace.json"
    "$ROOT/.cursor-plugin/marketplace.json"
)

echo ""
echo -e "${CYAN}=== Rosetta Version Bumper ===${RESET}"
echo ""
echo "Current versions:"
for f in "${TOML_FILES[@]}"; do
    printf "  %-50s %s\n" "[toml] ${f#$ROOT/}" "$(get_toml_version "$f")"
done
for f in "${PLUGIN_FILES[@]}"; do
    printf "  %-50s %s\n" "[plugin.json] ${f#$ROOT/}" "$(get_json_version "$f")"
done
for f in "${MARKETPLACE_FILES[@]}"; do
    printf "  %-50s %s\n" "[marketplace.json] ${f#$ROOT/}" "$(get_json_version "$f")"
done

echo ""
echo "Bump type:"
echo "  [1] patch   [2] minor   [3] major   [4] custom"
read -r -p "Choose (default: 1 = patch): " bump_choice
bump_choice="${bump_choice:-1}"

ref_version="$(get_toml_version "${TOML_FILES[0]}")"

case "$bump_choice" in
    1) NEW_VERSION="$(bump_semver "$ref_version" patch)" ;;
    2) NEW_VERSION="$(bump_semver "$ref_version" minor)" ;;
    3) NEW_VERSION="$(bump_semver "$ref_version" major)" ;;
    4)
        read -r -p "Enter new version (e.g. 2.1.0): " NEW_VERSION
        if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Invalid semver format. Expected X.Y.Z"
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}New version: $NEW_VERSION${RESET}"
echo ""

# --- pyproject.toml ---
echo "--- pyproject.toml files ---"
for f in "${TOML_FILES[@]}"; do
    current="$(get_toml_version "$f")"
    rel="${f#$ROOT/}"
    if ask_yn "Bump $rel  ($current → $NEW_VERSION)?" "y"; then
        sedi "s/^version = \"${current}\"/version = \"${NEW_VERSION}\"/" "$f"
        echo -e "  ${GREEN}Updated${RESET}"
    else
        echo "  Skipped"
    fi
done

echo ""
# --- plugin.json ---
echo "--- plugin.json files ---"
for f in "${PLUGIN_FILES[@]}"; do
    current="$(get_json_version "$f")"
    rel="${f#$ROOT/}"
    if ask_yn "Bump $rel  ($current → $NEW_VERSION)?" "y"; then
        sedi "s/\"version\": \"${current}\"/\"version\": \"${NEW_VERSION}\"/g" "$f"
        echo -e "  ${GREEN}Updated${RESET}"
    else
        echo "  Skipped"
    fi
done

echo ""
# --- marketplace.json (default N) ---
echo "--- marketplace.json files (default: N) ---"
for f in "${MARKETPLACE_FILES[@]}"; do
    current="$(get_json_version "$f")"
    rel="${f#$ROOT/}"
    if ask_yn "Bump $rel  ($current → $NEW_VERSION)?" "n"; then
        sedi "s/\"version\": \"${current}\"/\"version\": \"${NEW_VERSION}\"/g" "$f"
        echo -e "  ${GREEN}Updated${RESET}"
    else
        echo "  Skipped"
    fi
done

echo ""
echo -e "${GREEN}Done!${RESET}"
echo ""
