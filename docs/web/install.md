---
layout: default
title: Install
permalink: /install/
---

<section class="hero">
  <h1>Installation</h1>
  <p>Install Rosetta MCP in your preferred coding assistant.</p>
</section>

## Prerequisites

- Python 3.12+
- `uvx` (from `uv`)
- An MCP-capable client: Cursor, Claude Code, Codex, VS Code, Windsurf, etc.

## Install MCP Server

Use `uvx ims-mcp@latest` in your client configuration. The only differences are client-specific config file shape and environment variable placement.

## Verify Setup

1. Restart/reload your AI client after config changes.
2. Ask the assistant to confirm MCP tools are available.
3. Run a small request that should trigger instruction loading and classification.

<div class="note">Use your IDE's MCP settings and add <code>uvx ims-mcp@latest</code> with required environment variables.</div>
