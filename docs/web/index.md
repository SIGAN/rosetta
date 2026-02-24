---
layout: default
title: Home
permalink: /
---

<section class="hero">
  <img src="{{ '/assets/brand/Rosetta-Icon-With-Text.png' | relative_url }}" alt="Rosetta" style="max-width: 220px; width: 100%; height: auto; margin-bottom: .7rem;">
  <h1>Rosetta</h1>
  <p>A control plane for AI-agent behavior and shared engineering context.</p>
</section>

<section class="grid">
  <article class="card">
    <h3>Start Here</h3>
    <p>Read the <a href="{{ '/overview/' | relative_url }}">project overview</a> first, then follow <a href="{{ '/install/' | relative_url }}">installation</a> and <a href="{{ '/usage/' | relative_url }}">usage</a>.</p>
  </article>
  <article class="card">
    <h3>What This Covers</h3>
    <p>Rules-as-code, request classification, MCP-driven context loading, and release-based governance for instructions.</p>
  </article>
</section>

## High-Level Plan

<div class="grid">
  <article class="card">
    <h3>Rules Modernization</h3>
    <ol>
      <li>Normalize and simplify instruction taxonomy (agents, workflows, skills, rules).</li>
      <li>Keep progressive disclosure and classification-first flow as defaults.</li>
      <li>Harden guardrails and validation criteria for predictable execution quality.</li>
    </ol>
  </article>
  <article class="card">
    <h3>RAGFlow Adoption</h3>
    <ol>
      <li>Standardize on RAGFlow datasets and API-key auth.</li>
      <li>Keep metadata and hash-based publishing for fast incremental updates.</li>
      <li>Use two-stage filtering for precise retrieval in MCP tools.</li>
    </ol>
  </article>
</div>

