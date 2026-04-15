---
name: lsp-install
description: "Rosetta skill for installing Language Server Protocol servers based on detected tech stack. Use when initializing workspace with LSP support enabled or when explicitly requesting LSP installation."
baseSchema: docs/schemas/skill.md
license: Apache-2.0
user-invocable: true
argument-hint: "languages (optional, comma-separated: typescript,python,go)"
model: claude-haiku-4-5, gemini-3-flash-preview
tags: ["lsp", "installation", "workspace-init", "language-server"]
---

<lsp_install>

<role>

LSP installation specialist — detects tech stack, maps to language servers, installs idempotently with verification.

</role>

<when_to_use_skill>

Without LSP, AI agents treat source files as plain text. Invoked from init-workspace-flow after discovery phase — prompts user for approval before installation.

</when_to_use_skill>

<core_concepts>

- Rosetta prep steps completed
- LSP provides AI agents with: type info, cross-references, diagnostics, refactoring
- Strictly opt-in: never install without explicit user consent
- Idempotent: safe to re-run, skips already-installed servers
- Prerequisite-aware: checks for npm/pip/go/rustup before installation

</core_concepts>

<process>

1. Detect languages:
   a. If docs/TECHSTACK.md exists (from init-workspace-discovery): parse for languages
   b. Fallback: detect via file patterns (package.json→TS/JS, pyproject.toml→Python, go.mod→Go, etc.)
2. Prompt user: "Install LSP servers for [detected languages]? This improves AI code quality. (recommended)"
3. If user declines: exit gracefully
4. ACQUIRE `lsp-install/assets/li-detection-map.md` FROM KB
5. For each detected language:
   a. Map to LSP server using detection map
   b. Check if already installed via verification command
   c. If installed: report as installed, skip
   d. If not installed: check prerequisites, run installation script
   e. Verify installation success
6. Report results: installed, skipped, failed (with reasons)
7. If any installation failed: provide troubleshooting guidance

</process>

<validation_checklist>

- [ ] Opt-in verified before any installation
- [ ] Each language maps to exactly one LSP server
- [ ] Prerequisites checked before installation attempt
- [ ] Verification command confirms installation
- [ ] Failures reported with actionable guidance

</validation_checklist>

<best_practices>

- Check prerequisites before installation (npm for TS, pip for Python, go for Go, rustup for Rust, java for Java/Kotlin)
- Use global installation where appropriate (npm -g, pip install)
- Prefer rustup component for rust-analyzer (managed updates)
- Log all installation output for troubleshooting

</best_practices>

<pitfalls>

- jdtls requires Java 21+; kotlin-lsp requires Java 17+ — check java version first
- OmniSharp requires .NET 6.0+ or Mono 6.4.0+ on macOS/Linux
- Do not block workflow on installation failure — report and continue
- Windows: some installation commands differ (use PowerShell equivalents)

</pitfalls>

<resources>

- asset `lsp-install/assets/li-detection-map.md` — language to LSP mapping
- asset `lsp-install/assets/li-install-scripts.md` — installation commands per language
- asset `lsp-install/assets/li-readme-section.md` — README documentation for LSP support
- skill `init-workspace-discovery` — produces TECHSTACK.md for language detection (preferred source)

</resources>

</lsp_install>
