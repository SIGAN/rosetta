---
layout: default
title: Overview
permalink: /overview/
---

<section class="hero">
  <h1>Overview</h1>
  <p>Rosetta provides shared prompts and rules that stay consistent across IDEs and coding agents.</p>
</section>

## What Rosetta Solves

- Centralized governance for AI instructions and workflows.
- Consistent behavior across Cursor, Claude Code, Codex, Copilot, and others.
- Project-aware assistance via MCP and knowledge retrieval.

## Core Principles

<div class="grid">
  <article class="card"><h3>Classification First</h3><p>Requests map to specific workflows (coding, QA, research, modernization, help, and others).</p></article>
  <article class="card"><h3>Progressive Disclosure</h3><p>Load only what is needed to reduce context bloat and execution drift.</p></article>
  <article class="card"><h3>Evidence Based</h3><p>Drive outputs from documented context, assumptions, and explicit validation.</p></article>
</div>

## Architecture Snapshot

- **Content:** markdown instructions and project/business context.
- **Publish pipeline:** CLI tools prepare metadata and publish to RAGFlow datasets.
- **Consumption:** MCP tools retrieve and inject context into AI sessions.
- **Release model:** r1/r2/r3 tracks safe evolution and rollback.

<div class="note">
  Minimal attribution note: Rosetta originated in enterprise delivery practice; this site focuses on product behavior and usage.
</div>
