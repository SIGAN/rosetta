---
layout: default
title: Usage
permalink: /usage/
---

<section class="hero">
  <h1>Usage Guide</h1>
  <p>How to work with Rosetta in day-to-day development tasks.</p>
</section>

## How It Works

1. Bootstrap instructions load first.
2. Your request is classified into a mode.
3. Only relevant instruction packs are loaded.
4. The assistant executes with guardrails and validation.

## Main Request Modes

<div class="grid">
  <article class="card"><h3>Coding</h3><p>Implementation, bug fixes, refactors, and config changes.</p></article>
  <article class="card"><h3>Automated QA</h3><p>Test strategy, scenario design, implementation, and reporting.</p></article>
  <article class="card"><h3>Research</h3><p>Investigation and technical discovery without code changes.</p></article>
  <article class="card"><h3>Modernization</h3><p>Large migrations and re-architecture programs.</p></article>
  <article class="card"><h3>Code Analysis</h3><p>Understand and explain existing systems and implementation details.</p></article>
  <article class="card"><h3>Help</h3><p>How to use Rosetta capabilities and workflows themselves.</p></article>
</div>

## Usage Pattern

- Describe intent naturally; classification should route the workflow.
- Prefer explicit constraints, acceptance criteria, and risk boundaries.
- For risky or destructive actions, require explicit human approval.
