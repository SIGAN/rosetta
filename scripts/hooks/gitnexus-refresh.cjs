#!/usr/bin/env node
/**
 * GitNexus async re-index hook (PostToolUse)
 *
 * Fires silently after every Edit / Write / MultiEdit tool call.
 * Spawns `gitnexus analyze` detached in the background with a 5-second
 * debounce so multi-file edit waves coalesce into one re-index.
 *
 * Rules:
 *  - No stdout output — the agent must never see this hook.
 *  - Logs go to ~/.cache/gitnexus/refresh.log only.
 *  - No-ops immediately if .gitnexus/ is not found in the repo tree.
 *  - Opt-in: only active when installed by the user (not auto-loaded).
 *
 * Installation (Claude Code):
 *   Add to ~/.claude.json or .claude/settings.json:
 *   {
 *     "hooks": {
 *       "PostToolUse": [{
 *         "matcher": "Edit|Write|MultiEdit",
 *         "hooks": [{ "type": "command", "command": "node /path/to/gitnexus-refresh.cjs" }]
 *       }]
 *     }
 *   }
 */

'use strict';

const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

// ── helpers ──────────────────────────────────────────────────────────────────

function readInput() {
  try {
    return JSON.parse(fs.readFileSync(0, 'utf-8'));
  } catch {
    return {};
  }
}

/**
 * Walk up from startDir looking for a .gitnexus directory.
 * Returns its parent (the repo root) or null if not found.
 */
function findRepoRoot(startDir) {
  let dir = startDir || process.cwd();
  for (let i = 0; i < 10; i++) {
    if (fs.existsSync(path.join(dir, '.gitnexus'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

function ensureCacheDir() {
  const dir = path.join(os.homedir(), '.cache', 'gitnexus');
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function log(cacheDir, message) {
  try {
    const ts = new Date().toISOString();
    fs.appendFileSync(path.join(cacheDir, 'refresh.log'), `${ts}  ${message}\n`);
  } catch {
    // logging must never crash the hook
  }
}

// ── debounce ─────────────────────────────────────────────────────────────────

const DEBOUNCE_MS = 5000;

/**
 * Returns true if enough time has passed since the last re-index trigger.
 * Writes a new stamp file when returning true.
 */
function shouldTrigger(cacheDir, repoRoot) {
  // Use a hash of the repo root path as the key so each repo gets its own stamp.
  const key = Buffer.from(repoRoot).toString('base64').replace(/[/+=]/g, '_');
  const stampFile = path.join(cacheDir, `${key}.lastrun`);

  try {
    const stat = fs.statSync(stampFile);
    if (Date.now() - stat.mtimeMs < DEBOUNCE_MS) return false;
  } catch {
    // stamp doesn't exist yet — first run
  }

  // Touch the stamp file
  fs.writeFileSync(stampFile, String(Date.now()));
  return true;
}

// ── spawn ────────────────────────────────────────────────────────────────────

function spawnAnalyze(repoRoot, cacheDir) {
  // Detect whether embeddings were generated last time.
  let hadEmbeddings = false;
  try {
    const meta = JSON.parse(
      fs.readFileSync(path.join(repoRoot, '.gitnexus', 'meta.json'), 'utf-8')
    );
    hadEmbeddings = !!(meta.stats && meta.stats.embeddings > 0);
  } catch {
    // no meta — proceed without embeddings flag
  }

  const args = hadEmbeddings
    ? ['gitnexus', 'analyze', '--embeddings']
    : ['gitnexus', 'analyze'];

  const logFile = path.join(cacheDir, 'refresh.log');
  const out = fs.openSync(logFile, 'a');

  const child = spawn('npx', args, {
    cwd: repoRoot,
    detached: true,
    stdio: ['ignore', out, out],
  });

  child.unref();
  fs.closeSync(out);
}

// ── main ─────────────────────────────────────────────────────────────────────

function main() {
  const input = readInput();

  // Only handle PostToolUse for file-mutating tools
  if (input.hook_event_name !== 'PostToolUse') return;
  const tool = input.tool_name || '';
  if (!/^(Edit|Write|MultiEdit)$/.test(tool)) return;

  const cwd      = input.cwd || process.cwd();
  const repoRoot = findRepoRoot(cwd);
  if (!repoRoot) return; // GitNexus not initialised in this repo

  const cacheDir = ensureCacheDir();

  if (!shouldTrigger(cacheDir, repoRoot)) return; // debounced

  log(cacheDir, `[gitnexus-refresh] triggering analyze (tool=${tool}, cwd=${cwd})`);
  spawnAnalyze(repoRoot, cacheDir);
}

main();
