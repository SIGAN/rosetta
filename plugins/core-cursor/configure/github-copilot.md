---
name: github-copilot
description: GitHub Copilot configuration guide for skills, rules, workflows, custom agents, and MCP integration through repository-committed configuration files.
---

# GitHub Copilot - Skills, Rules, Workflows Configuration Guide - 2026

## Configuration Files

- **`.github/copilot-instructions.md`** - Repository-wide instructions (CORE root rule) - Markdown
- **`.github/instructions/*.instructions.md`** - Path-specific instructions - Markdown + YAML frontmatter
- **`.github/agents/*.agent.md`** - Custom agents - Markdown + YAML frontmatter
- **`.github/skills/*/SKILL.md`** - Project-level agent skills - Markdown + YAML frontmatter
- **`.github/workflows/copilot-setup-steps.yml`** - Environment setup - GitHub Actions YAML
- **`.vscode/mcp.json`** - MCP server integration - JSON

---

## Repository-Wide Instructions

**CRITICAL** The CORE root rule file is `.github/copilot-instructions.md`.

**File:** `.github/copilot-instructions.md` 

**Format:** Markdown (natural language, no frontmatter)

**Structure:**

```markdown
# Project Coding Standards

## General Guidelines

- Use TypeScript for all new files
- Follow functional programming principles

## Security

- Never commit API keys or secrets
- Validate all user inputs
```

**Notes:**

- Use workspace relative references in the main instruction file to add any other documents and instructions.

---

## Path-Specific Instructions

**Location:** `.github/instructions/[name].instructions.md`

**Format:** Markdown with YAML frontmatter (filename MUST end with `.instructions.md`)

**Structure:**

```markdown
---
applyTo: "src/api/**/*.ts"
---

# Backend API Guidelines

## Request Handling

- Validate all incoming requests using Zod schemas
- Return consistent error responses with status codes

## Security

- Implement rate limiting on all endpoints
- Use JWT tokens for authentication
```

---

## Custom Agents

**Location:** `.github/agents/[agent-name].agent.md`

**Invocation:** `@agent-name` in Copilot Chat

**Format:** Markdown with YAML frontmatter (filename MUST end with `.agent.md`)

**Frontmatter Fields:**

- `name`: Agent identifier (lowercase-with-hyphens)
- `description`: Brief purpose description
- `tools`: Tool array (optional)
- `mcp-servers`: MCP configs (optional)

**Tool Aliases:**

- `"read"`, `"edit"`, `"search"`, `"shell"`, `"custom-agent"`, `"web"`
- `"*"` - All tools
- `"github/*"` - MCP server tools
- `"playwright/navigate"` - Specific MCP tool

**Structure:**

```markdown
---
name: code-reviewer
description: Expert code reviewer for quality, security, and maintainability
tools: ["read", "search"]
---

You are a senior code reviewer ensuring high standards. When invoked:

1. Analyze code for readability and maintainability
2. Check for security vulnerabilities

Provide specific, actionable feedback with examples.
```

---

## Agent Skills

**Location:** `.github/skills/[skill-name]/SKILL.md` or `.claude/skills/[skill-name]/SKILL.md`

**Works with:** Copilot coding agent, GitHub Copilot CLI, VS Code Insiders agent mode

**Format:** Markdown with YAML frontmatter (file must be named `SKILL.md`)

**Frontmatter Fields:**

- `name`: Skill identifier (required, lowercase-with-hyphens)
- `description`: What the skill does and when to use it (required)
- `license`: License information (optional)

**Structure:**

```markdown
---
name: github-actions-failure-debugging
description: Guide for debugging failing GitHub Actions workflows. Use this when asked to debug failing GitHub Actions workflows.
---

To debug failing GitHub Actions workflows in a pull request:

1. Use the `list_workflow_runs` tool to look up recent workflow runs for the pull request and their status
2. Use the `summarize_job_log_failures` tool to get an AI summary of the logs for failed jobs
3. If you still need more information, use the `get_job_logs` or `get_workflow_run_logs` tool to get the full detailed failure logs
4. Try to reproduce the failure yourself in your own environment
5. Fix the failing build
```

**Notes:**

- Each skill must be in its own directory
- Directory name should match the `name` in frontmatter
- Can include additional scripts, examples, or resources in the skill directory
- Copilot automatically loads skills based on task relevance and skill description
- Skills vs Instructions: Use instructions for simple rules relevant to all tasks, skills for detailed task-specific procedures

---

## Environment Setup

**File:** `.github/workflows/copilot-setup-steps.yml`

**Format:** GitHub Actions workflow

**Structure:**

```yaml
name: Copilot Setup Steps

on:
  workflow_dispatch:

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

---

## MCP Integration

**File:** `.vscode/mcp.json`

**Format:** JSON

**Structure:**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    }
  }
}
```

---

## Built-in Slash Commands

**Note:** Custom slash commands are NOT supported.

Available commands:

- `/doc` - Insert documentation comments
- `/explain` - Explain selected code
- `/fix` - Fix bugs or errors
- `/tests` - Generate unit tests
- `/generate` - Generate new code snippets
- `/optimize` - Recommend code optimizations
- `/help` - Show available commands
- `/exp` - Start new conversation with fresh context
- `/new` - Set up new projects
- `/newNotebook` - Set up new Jupyter notebooks

---

## Project File Structure

```
project-root/
├── .github/
│   ├── copilot-instructions.md          # CORE root rule
│   ├── agents/
│   │   └── [agent-name].agent.md
│   ├── instructions/
│   │   └── [rule-name].instructions.md
│   ├── skills/
│   │   └── [skill-name]/
│   │       ├── SKILL.md                 # Required filename
│   │       └── [optional-resources]
│   └── workflows/
│       └── copilot-setup-steps.yml
└── .vscode/
    ├── mcp.json
    └── settings.json
```

---

## VS Code Settings (Project-Level)

**File:** `.vscode/settings.json`

**Structure:**

```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": false
  },
  "editor.inlineSuggest.enabled": true
}
```
