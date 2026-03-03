---
layout: default
title: Home
permalink: /
---

<!-- ===== HERO ===== -->
<section class="hero-main">
  <img src="{{ '/assets/brand/rosetta-logo-full-color-white-text.png' | relative_url }}" alt="Rosetta logo" class="hero-logo logo-dark">
  <img src="{{ '/assets/brand/rosetta-logo-full-color-black-text.png' | relative_url }}" alt="Rosetta logo" class="hero-logo logo-light">
  <p class="hero-tagline">Control plane for AI coding agents. Governs behavior, packages proven workflows, and delivers consistent engineering quality across your entire organization.</p>
  <div class="hero-actions">
    <a href="#quick-start" class="button">Get Started</a>
    <a href="{{ '/overview/' | relative_url }}" class="button-ghost">Learn More</a>
    <a href="https://github.com/griddynamics/rosetta" class="button-ghost" target="_blank" rel="noopener noreferrer">GitHub</a>
  </div>
</section>

<!-- ===== QUICK START ===== -->
<section class="section" id="quick-start">
  <div class="qs-panel">
    <h2 class="with-marker">Quick Start</h2>
    <p class="qs-sub">Add Rosetta MCP to your AI coding client in minutes. No source code sharing required.</p>

    <div class="qs-tabs" role="tablist">
      <button class="qs-tab active" data-tab="cli" role="tab">Rosetta CLI <span class="qs-tab-badge">Recommended</span></button>
      <button class="qs-tab" data-tab="claude" role="tab">Claude Code</button>
      <button class="qs-tab" data-tab="cursor" role="tab">Cursor / Windsurf</button>
      <button class="qs-tab" data-tab="vscode" role="tab">VS Code / Copilot</button>
      <button class="qs-tab" data-tab="other" role="tab">JetBrains / Other</button>
    </div>

    <!-- Tab: Rosetta CLI (Recommended) -->
    <div class="qs-content active" id="qs-cli">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> brew install uv          <span class="qs-comment"># macOS</span>
<span class="qs-prompt">$</span> curl -LsSf https://astral.sh/uv/install.sh | sh  <span class="qs-comment"># Linux / Windows (WSL)</span></pre>
      </div>
      <p class="qs-step-label">Step 2 — Configure all supported IDEs</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> npx rosetta configure</pre>
        <button class="qs-copy" data-copy="npx rosetta configure">Copy</button>
      </div>
      <p class="qs-step-label">Step 3 — Initialize your repository</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart your IDE, then ask your assistant:</span>
<span class="qs-comment"># "Initialize this repository"</span></pre>
      </div>
      <p class="qs-step-label">Step 4 — Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Ask your assistant:</span>
<span class="qs-comment"># "What can you do?"</span></pre>
      </div>
    </div>

    <!-- Tab: Claude Code -->
    <div class="qs-content" id="qs-claude">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> brew install uv          <span class="qs-comment"># macOS</span>
<span class="qs-prompt">$</span> curl -LsSf https://astral.sh/uv/install.sh | sh  <span class="qs-comment"># Linux</span></pre>
      </div>
      <p class="qs-step-label">Step 2 — Add Rosetta MCP</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> claude mcp add --transport stdio KnowledgeBase \
    --env R2R_API_BASE=https://ims-r2r-dev.evergreen.gcp.griddynamics.net/ \
    --env R2R_COLLECTION=aia-r2 \
    --env R2R_EMAIL=***REMOVED*** \
    --env R2R_PASSWORD=***REMOVED*** \
    -- uvx ims-mcp</pre>
        <button class="qs-copy" data-copy="claude mcp add --transport stdio KnowledgeBase --env R2R_API_BASE=https://ims-r2r-dev.evergreen.gcp.griddynamics.net/ --env R2R_COLLECTION=aia-r2 --env R2R_EMAIL=***REMOVED*** --env R2R_PASSWORD=***REMOVED*** -- uvx ims-mcp">Copy</button>
      </div>
      <p class="qs-step-label">Step 3 — Initialize your repository</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart Claude Code, then ask your assistant:</span>
<span class="qs-comment"># "Initialize this repository"</span></pre>
      </div>
      <p class="qs-step-label">Step 4 — Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Ask your assistant:</span>
<span class="qs-comment"># "What can you do?"</span></pre>
      </div>
    </div>

    <!-- Tab: Cursor / Windsurf -->
    <div class="qs-content" id="qs-cursor">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> brew install uv          <span class="qs-comment"># macOS</span>
<span class="qs-prompt">$</span> curl -LsSf https://astral.sh/uv/install.sh | sh  <span class="qs-comment"># Linux</span></pre>
      </div>
      <p class="qs-step-label">Step 2 — Add to MCP config</p>
      <p class="qs-sub" style="margin:.3rem 0 .6rem;font-size:.82rem;">Cursor: <code style="font-size:.82rem;">~/.cursor/mcp.json</code> &nbsp;·&nbsp; Windsurf: MCP settings in IDE</p>
      <div class="qs-code-wrap">
        <pre class="qs-code">{
  "mcpServers": {
    "KnowledgeBase": {
      "command": "uvx",
      "args": ["ims-mcp@latest"],
      "env": {
        "R2R_API_BASE": "https://ims-r2r-dev.evergreen.gcp.griddynamics.net/",
        "R2R_COLLECTION": "aia-r2",
        "R2R_EMAIL": "***REMOVED***",
        "R2R_PASSWORD": "***REMOVED***"
      }
    }
  }
}</pre>
      </div>
      <p class="qs-step-label">Step 3 — Initialize &amp; Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart your IDE, then ask your assistant:</span>
<span class="qs-comment"># "Initialize this repository"  →  "What can you do?"</span></pre>
      </div>
    </div>

    <!-- Tab: VS Code / Copilot -->
    <div class="qs-content" id="qs-vscode">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> brew install uv          <span class="qs-comment"># macOS</span>
<span class="qs-prompt">$</span> curl -LsSf https://astral.sh/uv/install.sh | sh  <span class="qs-comment"># Linux</span></pre>
      </div>
      <p class="qs-step-label">Step 2 — Add to <code style="font-size:.82rem;">.vscode/mcp.json</code></p>
      <div class="qs-code-wrap">
        <pre class="qs-code">{
  "servers": {
    "KnowledgeBase": {
      "type": "stdio",
      "command": "uvx",
      "args": ["ims-mcp@latest"],
      "env": {
        "R2R_API_BASE": "https://ims-r2r-dev.evergreen.gcp.griddynamics.net/",
        "R2R_COLLECTION": "aia-r2",
        "R2R_EMAIL": "***REMOVED***",
        "R2R_PASSWORD": "***REMOVED***"
      }
    }
  }
}</pre>
      </div>
      <p class="qs-step-label">Step 3 — Initialize &amp; Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart VS Code, then ask Copilot:</span>
<span class="qs-comment"># "Initialize this repository"  →  "What can you do?"</span></pre>
      </div>
    </div>

    <!-- Tab: JetBrains / Other -->
    <div class="qs-content" id="qs-other">
      <p class="qs-step-label">Step 1 — Install uv</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-prompt">$</span> brew install uv          <span class="qs-comment"># macOS</span>
<span class="qs-prompt">$</span> curl -LsSf https://astral.sh/uv/install.sh | sh  <span class="qs-comment"># Linux</span></pre>
      </div>
      <p class="qs-step-label">Step 2 — Add MCP config</p>
      <p class="qs-sub" style="margin:.3rem 0 .6rem;font-size:.82rem;">JetBrains Copilot: <code style="font-size:.82rem;">~/.config/github-copilot/intellij/mcp.json</code></p>
      <div class="qs-code-wrap">
        <pre class="qs-code">{
  "servers": {
    "KnowledgeBase": {
      "command": "uvx",
      "args": ["ims-mcp@latest"],
      "type": "stdio",
      "env": {
        "R2R_API_BASE": "https://ims-r2r-dev.evergreen.gcp.griddynamics.net/",
        "R2R_COLLECTION": "aia-r2",
        "R2R_EMAIL": "***REMOVED***",
        "R2R_PASSWORD": "***REMOVED***"
      }
    }
  }
}</pre>
      </div>
      <p class="qs-step-label">Step 3 — Initialize &amp; Verify</p>
      <div class="qs-code-wrap">
        <pre class="qs-code"><span class="qs-comment"># Restart your IDE, then ask your assistant:</span>
<span class="qs-comment"># "Initialize this repository"  →  "What can you do?"</span></pre>
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

<!-- ===== KEY FEATURES ===== -->
<section class="section">
  <h2 class="with-marker">Key Features</h2>
  <ul class="features-list">
    <li>Based on SOTA Meta-Prompting technology</li>
    <li>Project-specific, dynamically composed context</li>
    <li>Replaces static, one-size-fits-all rule sets</li>
    <li>Progressive disclosure</li>
    <li>Air gap security — no source code is transferred</li>
    <li>MCP-based: one-line installation &amp; centralized management</li>
    <li>Agent agnostic: Claude Code, Cursor, Codex, and more</li>
    <li>Rich dynamic context with rules, workflows, skills, and sub-agents</li>
    <li>Continuously updated centralized knowledge base</li>
    <li>Cloud, on-prem, open source, and enterprise editions</li>
  </ul>
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
