---
layout: default
title: Overview
permalink: /overview/
---

<section class="hero">
  <h1>Overview</h1>
  <p>Rosetta provides shared prompts and rules that stay consistent across IDEs, coding agents, and models. It uses a classification-first and meta-prompting approach so teams can run project-specific workflows with predictable quality.</p>
</section>

## What Rosetta Solves

- Centralized governance for AI instructions and workflows.
- Consistent behavior across Cursor, Claude Code, Codex, Copilot, and others.
- Project-aware assistance via MCP and knowledge retrieval.

## Core Principles

<div class="grid">
  <article class="card"><h3>Agent-Agnostic</h3><p>Works across Cursor, Claude Code, Copilot, and other MCP-capable tools with consistent behavior.</p></article>
  <article class="card"><h3>Classification First</h3><p>Requests map to explicit workflows (coding, QA, research, modernization, help, and others).</p></article>
  <article class="card"><h3>Progressive Disclosure</h3><p>Load only the required instructions and context to reduce token waste and execution drift.</p></article>
  <article class="card"><h3>Meta-Prompting</h3><p>Adapts prompts and rules to project context rather than relying on static one-off prompt snippets.</p></article>
  <article class="card"><h3>Evidence Based</h3><p>Ground outputs in documented context, assumptions, and explicit validation steps.</p></article>
  <article class="card"><h3>Release Driven</h3><p>Evolve safely with release-based governance and rollback-friendly instruction management.</p></article>
</div>

## Key Features

<div class="grid">
  <article class="card"><h3>Unified Knowledge Hub</h3><p>Business context, architecture, requirements, and rules are organized in one retrievable system.</p></article>
  <article class="card"><h3>RAGFlow Integration</h3><p>Publishes instruction artifacts for semantic retrieval via MCP tools in coding sessions.</p></article>
  <article class="card"><h3>Smart Metadata and Incremental Updates</h3><p>Uses tags and hash-based change detection to publish only modified files.</p></article>
  <article class="card"><h3>Built-in Guardrails</h3><p>Includes approval gates, risk controls, and validation checkpoints for safer execution.</p></article>
  <article class="card"><h3>Single-Command Onboarding</h3><p>Supports fast initialization, upgrades, and project-level customization.</p></article>
  <article class="card"><h3>Community-Friendly</h3><p>Open-source workflow with contribution paths for improvements to rules and guidance.</p></article>
</div>

## Architecture Snapshot

- **Content:** markdown instructions and project/business context.
- **Publish pipeline:** CLI tools prepare metadata and publish to RAGFlow datasets.
- **Consumption:** MCP tools retrieve and inject context into AI sessions.
- **Release model:** r1/r2/r3 tracks safe evolution and rollback.

<div class="note">
  Minimal attribution note: Rosetta originated in enterprise delivery practice; this site focuses on product behavior and usage.
</div>
