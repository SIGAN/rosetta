---
layout: default
title: Overview
permalink: /overview/
---

<section class="hero">
  <h1>What is Rosetta?</h1>
  <p>Rosetta is an enterprise-wide <strong>centralized control plane for AI coding agents</strong>. It delivers versioned instructions, business context, architecture knowledge, and proven workflows directly into every AI session — ensuring consistent, governed engineering across your entire organization.</p>
  <p class="muted">Built for teams where AI-assisted development is no longer optional — it's the default.</p>
</section>

---

## How It Works

<div class="ov-steps">
  <div class="ov-step">
    <span class="ov-step-num">01</span>
    <div>
      <strong>Install MCP</strong>
      <p>One command. Works with Claude Code, Cursor, Windsurf, VS Code, JetBrains, and any MCP-compatible tool. No source code sharing required.</p>
    </div>
  </div>
  <div class="ov-step">
    <span class="ov-step-num">02</span>
    <div>
      <strong>Initialize your repository</strong>
      <p>Ask your assistant <em>"Initialize this repository."</em> Rosetta analyzes your tech stack, architecture, and dependencies — then generates structured context files your agent uses in every session.</p>
    </div>
  </div>
  <div class="ov-step">
    <span class="ov-step-num">03</span>
    <div>
      <strong>Work with full context</strong>
      <p>Every request is project-aware from day one. Rules, conventions, and workflows are loaded automatically — consistently across every developer, every tool, every session.</p>
    </div>
  </div>
</div>

<div class="note">
  Agent-agnostic by design. Use <strong>Sonnet 4.5</strong> or better for optimal results. Current production release: <strong>r2</strong>.
</div>

---

## The Prepare → Research → Plan → Act Workflow

Rosetta structures every AI task into four deliberate phases, eliminating the trial-and-error loop that slows teams down:

<div class="workflow-schema">
  <div class="workflow-step">
    <div class="workflow-title">Prepare</div>
    <div class="workflow-desc">Load guardrails, coding conventions, and project-specific rules before touching any code. The agent knows the boundaries before it starts.</div>
    <ul class="workflow-points">
      <li>Agent rules &amp; guardrails</li>
      <li>Coding conventions</li>
      <li>Project context</li>
    </ul>
  </div>
  <div class="workflow-arrow" aria-hidden="true"></div>
  <div class="workflow-step">
    <div class="workflow-title">Research</div>
    <div class="workflow-desc">Semantically search the centralized knowledge base for architecture decisions, tech stack details, and prior solutions. No hallucination from missing context.</div>
    <ul class="workflow-points">
      <li>Architecture decisions</li>
      <li>Tech stack &amp; dependencies</li>
      <li>Prior solutions</li>
    </ul>
  </div>
  <div class="workflow-arrow" aria-hidden="true"></div>
  <div class="workflow-step">
    <div class="workflow-title">Plan</div>
    <div class="workflow-desc">Produce an explicit, reviewable plan grounded in your actual codebase and documented decisions — before executing a single change.</div>
    <ul class="workflow-points">
      <li>Explicit step-by-step plan</li>
      <li>Grounded in codebase</li>
      <li>Reviewable before action</li>
    </ul>
  </div>
  <div class="workflow-arrow" aria-hidden="true"></div>
  <div class="workflow-step">
    <div class="workflow-title">Act</div>
    <div class="workflow-desc">Execute with full context. Outputs are traceable, validated against project standards, and consistent with how your team actually works.</div>
    <ul class="workflow-points">
      <li>Context-aware execution</li>
      <li>Standards validation</li>
      <li>Traceable outputs</li>
    </ul>
  </div>
</div>

---

## Who It's For

<div class="ov-roles">
  <div class="rm-group">
    <div class="rm-label">Developers</div>
    <ul class="rm-list">
      <li>Project-aware agent from day one — no manual context setup</li>
      <li>Persistent, versioned rules that survive session restarts and team changes</li>
      <li>Shared context across teammates — no agent behavior drift</li>
      <li>Inspectable, diff-able instructions you can contribute back to</li>
    </ul>
  </div>
  <div class="rm-group">
    <div class="rm-label">Engineering Managers</div>
    <ul class="rm-list">
      <li>Standardized AI behavior across every team and every tool</li>
      <li>Centralized governance with rollback-friendly instruction releases</li>
      <li>Reduced onboarding time — new engineers inherit context instantly</li>
      <li>Air-gap security — no source code ever leaves your environment</li>
    </ul>
  </div>
  <div class="rm-group">
    <div class="rm-label">CTOs &amp; Architects</div>
    <ul class="rm-list">
      <li>Enterprise-wide enforcement of architecture standards and guardrails</li>
      <li>Rules-as-code: treat AI instructions like infrastructure — versioned and tested</li>
      <li>Evolve practices organization-wide with a single update to the knowledge base</li>
      <li>Agent-agnostic: no vendor lock-in, switch tools without losing context</li>
    </ul>
  </div>
</div>

---

## Core Principles

<dl class="ov-principles">
  <div class="ov-principle">
    <dt>Agent-Agnostic</dt>
    <dd>One MCP server, every client — Claude Code, Cursor, Windsurf, VS Code, JetBrains, OpenCode.</dd>
  </div>
  <div class="ov-principle">
    <dt>Meta-Prompting</dt>
    <dd>Dynamic prompt composition adapts instructions to project context, not static rule files.</dd>
  </div>
  <div class="ov-principle">
    <dt>Progressive Disclosure</dt>
    <dd>Load only what's relevant to the current task — less token waste, more focused responses.</dd>
  </div>
  <div class="ov-principle">
    <dt>Rules as Code</dt>
    <dd>AI instructions are versioned, reviewed, and deployed like software — with full rollback support.</dd>
  </div>
  <div class="ov-principle">
    <dt>Evidence-Based</dt>
    <dd>Every agent decision is grounded in documented architecture and project knowledge, not hallucination.</dd>
  </div>
  <div class="ov-principle">
    <dt>Air-Gap Security</dt>
    <dd>Only instructions and metadata travel over the wire. Your source code never leaves your environment.</dd>
  </div>
</dl>

---

## Architecture

Rosetta runs as a lightweight MCP server bridging your AI client with a centralized knowledge base:

<ul class="ov-arch">
  <li><strong>Knowledge Base</strong> — Markdown instructions and project context stored in a vector database for semantic retrieval.</li>
  <li><strong>MCP Server</strong> — <code>ims-mcp</code> runs locally via <code>uvx</code>. Your AI client calls it to pull contextually relevant instructions per task.</li>
  <li><strong>Context Files</strong> — On init, Rosetta writes <code>TECHSTACK.md</code>, <code>CODEMAP.md</code>, <code>DEPENDENCIES.md</code>, <code>ARCHITECTURE.md</code>, and <code>CONTEXT.md</code> into your repo.</li>
  <li><strong>Release Model</strong> — Instructions follow a release track (r1 → r2 → r3) for safe rollout, staged adoption, and rollback.</li>
  <li><strong>Collections</strong> — Each project or team targets its own knowledge collection with fine-grained scoping.</li>
</ul>

<script>
(function(){
  var principles = document.querySelectorAll('.ov-principle');
  var steps = document.querySelectorAll('.ov-step');

  if (!('IntersectionObserver' in window)) {
    principles.forEach(function(el) { el.classList.add('is-visible'); });
    steps.forEach(function(el) { el.classList.add('is-visible'); });
    return;
  }

  principles.forEach(function(el, i) { el.style.transitionDelay = (i * 0.12) + 's'; });
  steps.forEach(function(el, i) { el.style.transitionDelay = (i * 0.2) + 's'; });

  requestAnimationFrame(function() {
    requestAnimationFrame(function() {
      var obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            obs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

      principles.forEach(function(el) { obs.observe(el); });
      steps.forEach(function(el) { obs.observe(el); });
    });
  });
})();
</script>
