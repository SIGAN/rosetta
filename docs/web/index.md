---
layout: default
title: Home
permalink: /
---

<!-- ===== HERO ===== -->
<section class="hero-main">
  <img src="{{ '/assets/brand/rosetta-logo-full-color-white.png' | relative_url }}" alt="Rosetta logo" class="hero-logo">
  <h1>Rosetta</h1>
  <p class="hero-tagline">Control plane for AI coding agents. Governs behavior, packages proven workflows, and delivers consistent engineering quality across your entire organization.</p>
  <div class="hero-actions">
    <a href="{{ '/install/' | relative_url }}" class="button">Get Started</a>
    <a href="{{ '/overview/' | relative_url }}" class="button-ghost">Learn More</a>
    <a href="https://github.com/griddynamics/rosetta" class="button-ghost" target="_blank" rel="noopener noreferrer">GitHub</a>
  </div>
</section>

<!-- ===== QUICK START ===== -->
<section class="section">
  <div class="qs-panel">
    <h2 class="with-marker">Quick Start</h2>
    <p class="qs-sub">Add Rosetta MCP to your AI coding client in minutes. No source code sharing required.</p>

    <div class="qs-tabs" role="tablist">
      <button class="qs-tab active" data-tab="claude" role="tab">Claude Code</button>
      <button class="qs-tab" data-tab="ide" role="tab">Cursor / Windsurf / VS Code</button>
      <button class="qs-tab" data-tab="other" role="tab">Codex / Other</button>
    </div>

    <!-- Tab: Claude Code -->
    <div class="qs-content active" id="qs-claude">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> pip install uv</pre>
        <button class="qs-copy" data-copy="pip install uv">Copy</button>
      </div>
      <p class="qs-step-label">Step 2 — Add Rosetta MCP</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> claude mcp add rosetta -- uvx ims-mcp@latest</pre>
        <button class="qs-copy" data-copy="claude mcp add rosetta -- uvx ims-mcp@latest">Copy</button>
      </div>
      <p class="qs-step-label">Step 3 — Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart Claude Code, then ask your assistant:</span>
<span class="qs-comment"># "Confirm Rosetta MCP tools are available"</span></pre>
      </div>
    </div>

    <!-- Tab: Cursor / Windsurf / VS Code -->
    <div class="qs-content" id="qs-ide">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> pip install uv</pre>
        <button class="qs-copy" data-copy="pip install uv">Copy</button>
      </div>
      <p class="qs-step-label">Step 2 — Open MCP settings in your IDE and add</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> uvx ims-mcp@latest</pre>
        <button class="qs-copy" data-copy="uvx ims-mcp@latest">Copy</button>
      </div>
      <p class="qs-step-label">Step 3 — Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart your IDE, then ask your assistant:</span>
<span class="qs-comment"># "Confirm Rosetta MCP tools are available"</span></pre>
      </div>
    </div>

    <!-- Tab: Codex / Other -->
    <div class="qs-content" id="qs-other">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> pip install uv</pre>
        <button class="qs-copy" data-copy="pip install uv">Copy</button>
      </div>
      <p class="qs-step-label">Step 2 — Run the MCP server directly</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> uvx ims-mcp@latest</pre>
        <button class="qs-copy" data-copy="uvx ims-mcp@latest">Copy</button>
      </div>
      <p class="qs-step-label">Step 3 — Point your client at the server and verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Add the MCP server URL to your client config</span>
<span class="qs-comment"># then ask: "Confirm Rosetta MCP tools are available"</span></pre>
      </div>
    </div>

  </div>
</section>

<script>
(function() {
  document.querySelectorAll('.qs-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.qs-tab').forEach(function(t) { t.classList.remove('active'); });
      document.querySelectorAll('.qs-content').forEach(function(c) { c.classList.remove('active'); });
      tab.classList.add('active');
      document.getElementById('qs-' + tab.dataset.tab).classList.add('active');
    });
  });
  document.querySelectorAll('.qs-copy').forEach(function(btn) {
    btn.addEventListener('click', function() {
      navigator.clipboard.writeText(btn.dataset.copy).then(function() {
        var orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(function() { btn.textContent = orig; }, 1500);
      });
    });
  });
})();
</script>

<!-- ===== WHAT ROSETTA DOES ===== -->
<section class="section">
  <h2 class="with-marker">What Rosetta Does</h2>
  <div class="grid features-grid">
    <article class="card">
      <h3>Classification First</h3>
      <p>Every request maps to an explicit workflow — coding, QA, research, modernization, or help — for predictable, consistent execution.</p>
    </article>
    <article class="card">
      <h3>Meta-Prompting</h3>
      <p>Adapts prompts and rules to project-specific context instead of relying on static, one-off prompt snippets spread across teams.</p>
    </article>
    <article class="card">
      <h3>Agent-Agnostic</h3>
      <p>Works consistently across Cursor, Claude Code, GitHub Copilot, Codex, Windsurf, and any MCP-capable coding tool.</p>
    </article>
    <article class="card">
      <h3>Unified Knowledge Hub</h3>
      <p>Business context, architecture, requirements, and rules organized in one retrievable system via RAGFlow and MCP tools.</p>
    </article>
    <article class="card">
      <h3>Built-in Guardrails</h3>
      <p>Approval gates, risk controls, and human-in-the-loop checkpoints reduce AI slop and costly execution mistakes.</p>
    </article>
    <article class="card">
      <h3>Release Governance</h3>
      <p>r1/r2/r3 release tracks provide safe instruction evolution, rollback capability, and adoption visibility across teams.</p>
    </article>
  </div>
</section>


<!-- ===== WORKS WITH ===== -->
<section class="section">
  <h2 class="with-marker">Works With</h2>
  <p class="muted">Rosetta runs through any MCP-capable AI coding client. One setup, any tool, no vendor lock-in.</p>
  <div class="integrations-list">
    <span class="integration-tag">Cursor</span>
    <span class="integration-tag">Claude Code</span>
    <span class="integration-tag">GitHub Copilot</span>
    <span class="integration-tag">Windsurf</span>
    <span class="integration-tag">VS Code</span>
    <span class="integration-tag">Codex CLI</span>
    <span class="integration-tag">Any MCP Client</span>
  </div>
</section>

<div class="note">
  See <a href="{{ '/roadmap/' | relative_url }}">Roadmap</a> for current priorities and status. &nbsp;·&nbsp; <a href="{{ '/overview/' | relative_url }}">Read the full overview →</a>
</div>
