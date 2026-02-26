---
layout: default
title: Overview
permalink: /overview/
---

<section class="hero">
  <h1>Overview</h1>
  <p>Rosetta is a control plane for AI coding agents that automates context setup, enforces consistent workflows, and manages engineering knowledge at the organization level — without sharing your source code. It solves the core problems teams face with AI-assisted development:</p>
  <ul>
    <li>Fragmented adoption and inconsistent execution across teams and tools</li>
    <li>Missing business and technical context in day-to-day AI-assisted development</li>
    <li>Weak governance, low visibility, and avoidable risk in AI-enabled SDLC</li>
    <li>Reinvented workflows and slow onboarding between projects</li>
  </ul>
</section>

## Benefits By Role

<div class="grid">
  <article class="card">
    <h3>For Developers</h3>
    <ul>
      <li>Persistent, externalized agent context to keep behavior consistent across sessions</li>
      <li>Automatic setup of agent rules, workflows, and coding conventions per project</li>
      <li>Reduced manual prompt crafting and trial-and-error when switching tasks or repos</li>
      <li>Explicit, versioned context that can be inspected, diffed, and updated</li>
      <li>Shared context across teammates to avoid agent behavior drift</li>
    </ul>
  </article>
  <article class="card">
    <h3>For Managers</h3>
    <ul>
      <li>Security — no code is transferred, only rules</li>
      <li>Standardized AI agent behavior and centralized management of agent instructions</li>
      <li>Reduced onboarding time for new engineers and new codebases</li>
      <li>Clear ownership and evolution of AI development practices</li>
    </ul>
  </article>
</div>

## Core Principles

<div class="grid">
  <article class="card"><h3>Agent-Agnostic</h3><p>Works across Cursor, Claude Code, Copilot, and other MCP-capable tools with consistent behavior.</p></article>
  <article class="card"><h3>Classification First</h3><p>Requests map to explicit workflows (coding, QA, research, modernization, help, and others).</p></article>
  <article class="card"><h3>Progressive Disclosure</h3><p>Load only the required instructions and context to reduce token waste and execution drift.</p></article>
  <article class="card"><h3>Meta-Prompting</h3><p>Adapts prompts and rules to project context rather than relying on static one-off prompt snippets.</p></article>
  <article class="card"><h3>Evidence Based</h3><p>Ground outputs in documented context, assumptions, and explicit validation steps.</p></article>
  <article class="card"><h3>Release Driven</h3><p>Evolve safely with release-based governance and rollback-friendly instruction management.</p></article>
</div>

## Architecture Snapshot

- **Content:** markdown instructions and project/business context.
- **Publish pipeline:** CLI tools prepare metadata and publish to RAGFlow datasets.
- **Consumption:** MCP tools retrieve and inject context into AI sessions.
- **Release model:** r1/r2/r3 tracks safe evolution and rollback.

<div class="note">
  Minimal attribution note: Rosetta originated in enterprise delivery practice; this site focuses on product behavior and usage.
</div>
