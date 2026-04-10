'use strict';
// adapter.test.js — TDD test suite for adapter.js
// Run: node --test instructions/r2/core/hooks/adapter.test.js
//
// Expected results BEFORE adapter.js exists: ALL RED (module not found)
// Expected results AFTER adapter.js implemented:
//   - Claude Code tests: GREEN (~13)
//   - Stub IDE tests (Cursor/Codex/Windsurf/Copilot): RED (intentional, pending real fixtures)
//   - Error path tests: GREEN (~3)

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { Readable } = require('stream');

// Load fixtures
const FIXTURES_DIR = path.join(__dirname, 'test-fixtures');
const fx = (name) => require(path.join(FIXTURES_DIR, name));

const ccWrite     = fx('claude-code-post-tool-use-write.json');
const ccEdit      = fx('claude-code-post-tool-use-edit.json');
const ccBash      = fx('claude-code-pre-tool-use-bash.json');
const ccSubagent  = fx('claude-code-post-tool-use-write-subagent.json');
const fxCursor    = fx('cursor-post-tool-use-write.json');
const fxCodex     = fx('codex-post-tool-use-bash.json');
const fxWindsurf  = fx('windsurf-post-tool-use-write.json');
const fxCopilot   = fx('copilot-post-tool-use-write.json');
const fxUnknown   = fx('unknown-ide-input.json');

const { detectIDE, normalize, formatOutput, readStdin } = require('./adapter');

// ---------------------------------------------------------------------------
describe('detectIDE', () => {

  test('returns "claude-code" for PostToolUse Write input', () => {
    assert.equal(detectIDE(ccWrite), 'claude-code');
  });

  test('returns "claude-code" for PreToolUse Bash input', () => {
    assert.equal(detectIDE(ccBash), 'claude-code');
  });

  test('returns "claude-code" for subagent input (has agent_id)', () => {
    assert.equal(detectIDE(ccSubagent), 'claude-code');
  });

  // 🔴 RED until real Cursor fixture captured
  test('returns "cursor" for Cursor stub fixture', { todo: 'Replace stub with real Cursor stdin capture' }, () => {
    assert.equal(detectIDE(fxCursor), 'cursor');
  });

  test('returns "codex" for Codex PostToolUse Bash input', () => {
    assert.equal(detectIDE(fxCodex), 'codex');
  });

  // 🔴 RED until real Windsurf fixture captured
  test('returns "windsurf" for Windsurf stub fixture', { todo: 'Replace stub with real Windsurf stdin capture' }, () => {
    assert.equal(detectIDE(fxWindsurf), 'windsurf');
  });

  // 🔴 RED until real Copilot fixture captured
  test('returns "copilot" for Copilot stub fixture', { todo: 'Replace stub with real Copilot stdin capture' }, () => {
    assert.equal(detectIDE(fxCopilot), 'copilot');
  });

  test('throws for unknown IDE input shape', () => {
    assert.throws(() => detectIDE(fxUnknown), /Unsupported IDE/);
  });

  test('throws for null input', () => {
    assert.throws(() => detectIDE(null), /invalid|unsupported|null/i);
  });

  test('throws for empty object', () => {
    assert.throws(() => detectIDE({}), /Unsupported IDE/);
  });

});

// ---------------------------------------------------------------------------
describe('normalize', () => {

  test('Claude Code PostToolUse Write — identity pass-through', () => {
    const result = normalize(ccWrite);
    assert.deepEqual(result, ccWrite);
  });

  test('Claude Code PostToolUse Edit — identity pass-through', () => {
    const result = normalize(ccEdit);
    assert.deepEqual(result, ccEdit);
  });

  test('Claude Code PreToolUse Bash — identity (no tool_response)', () => {
    const result = normalize(ccBash);
    assert.deepEqual(result, ccBash);
    assert.equal(result.tool_response, undefined);
  });

  test('Claude Code subagent — preserves agent_id and agent_type', () => {
    const result = normalize(ccSubagent);
    assert.equal(result.agent_id, 'agent-456');
    assert.equal(result.agent_type, 'code-reviewer');
  });

  test('Claude Code — canonical fields all present', () => {
    const result = normalize(ccWrite);
    assert.ok(result.session_id, 'session_id missing');
    assert.ok(result.hook_event_name, 'hook_event_name missing');
    assert.ok(result.tool_name, 'tool_name missing');
    assert.ok(result.tool_use_id, 'tool_use_id missing');
    assert.ok(result.tool_input, 'tool_input missing');
    assert.ok(result.cwd, 'cwd missing');
    assert.ok(result.permission_mode, 'permission_mode missing');
  });

  // 🔴 RED until real Cursor fixture captured
  test('Cursor — transforms to canonical format', { todo: 'Replace stub with real Cursor stdin capture' }, () => {
    const result = normalize(fxCursor);
    assert.ok(result.hook_event_name);
    assert.ok(result.tool_name);
    assert.ok(result.tool_input);
  });

  test('Codex — identity pass-through, preserves model + turn_id', () => {
    const result = normalize(fxCodex);
    assert.ok(result.hook_event_name, 'hook_event_name missing');
    assert.ok(result.tool_name, 'tool_name missing');
    assert.ok(result.tool_input, 'tool_input missing');
    assert.equal(result.model, fxCodex.model, 'model not preserved');
    assert.equal(result.turn_id, fxCodex.turn_id, 'turn_id not preserved');
  });

  // 🔴 RED until real Windsurf fixture captured
  test('Windsurf — transforms to canonical format', { todo: 'Replace stub with real Windsurf stdin capture' }, () => {
    const result = normalize(fxWindsurf);
    assert.ok(result.hook_event_name);
    assert.ok(result.tool_name);
    assert.ok(result.tool_input);
  });

  // 🔴 RED until real Copilot fixture captured
  test('Copilot — transforms to canonical format', { todo: 'Replace stub with real Copilot stdin capture' }, () => {
    const result = normalize(fxCopilot);
    assert.ok(result.hook_event_name);
    assert.ok(result.tool_name);
    assert.ok(result.tool_input);
  });

  test('unknown IDE — throws', () => {
    assert.throws(() => normalize(fxUnknown), /Unsupported IDE/);
  });

});

// ---------------------------------------------------------------------------
describe('formatOutput', () => {

  test('PostToolUse additionalContext only — correct hookSpecificOutput shape', () => {
    const canonical = {
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: 'Test message'
      }
    };
    const result = formatOutput(canonical, 'claude-code');
    assert.deepEqual(result, canonical);
  });

  test('PostToolUse with all optional top-level fields — preserved', () => {
    const canonical = {
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: 'Test'
      },
      continue: true,
      stopReason: null,
      suppressOutput: false,
      systemMessage: 'hello'
    };
    const result = formatOutput(canonical, 'claude-code');
    assert.deepEqual(result, canonical);
  });

  test('PreToolUse deny decision — preserved', () => {
    const canonical = {
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: 'deny',
        permissionDecisionReason: 'Not allowed'
      }
    };
    const result = formatOutput(canonical, 'claude-code');
    assert.equal(result.hookSpecificOutput.permissionDecision, 'deny');
  });

  // 🔴 RED until real Cursor fixture captured
  test('Cursor — transforms output to Cursor format', { todo: 'Requires Cursor output schema from real capture' }, () => {
    const canonical = { hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } };
    const result = formatOutput(canonical, 'cursor');
    assert.ok(result);
  });

  test('Codex — output is identity pass-through (same schema as Claude Code)', () => {
    const canonical = { hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } };
    const result = formatOutput(canonical, 'codex');
    assert.deepEqual(result, canonical);
  });

  // 🔴 RED until real Windsurf fixture captured
  test('Windsurf — transforms output', { todo: 'Requires Windsurf output schema from real capture' }, () => {
    const canonical = { hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } };
    const result = formatOutput(canonical, 'windsurf');
    assert.ok(result);
  });

  // 🔴 RED until real Copilot fixture captured
  test('Copilot — transforms output', { todo: 'Requires Copilot output schema from real capture' }, () => {
    const canonical = { hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } };
    const result = formatOutput(canonical, 'copilot');
    assert.ok(result);
  });

});

// ---------------------------------------------------------------------------
describe('readStdin', () => {

  test('reads valid JSON from stdin stream — returns parsed object', async () => {
    const input = JSON.stringify(ccWrite);
    const stream = Readable.from([input]);
    const result = await readStdin(stream);
    assert.deepEqual(result, ccWrite);
  });

  test('reads empty stdin — throws with clear message', async () => {
    const stream = Readable.from(['']);
    await assert.rejects(readStdin(stream), /empty|no input|invalid/i);
  });

  test('reads invalid JSON — throws with clear message', async () => {
    const stream = Readable.from(['{ not valid json ']);
    await assert.rejects(readStdin(stream), /JSON|parse|invalid/i);
  });

});

// ---------------------------------------------------------------------------
describe('round-trip', () => {

  test('Claude Code Write: normalize → formatOutput → original shape', () => {
    const normalized = normalize(ccWrite);
    const output = formatOutput({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } }, 'claude-code');
    // Output schema is separate from input; verify input round-trip is identity
    assert.deepEqual(normalized, ccWrite);
    assert.ok(output.hookSpecificOutput);
  });

  // 🔴 RED until real Cursor fixture captured
  test('Cursor round-trip: normalize → formatOutput matches Cursor shape', { todo: 'Requires real Cursor capture' }, () => {
    const normalized = normalize(fxCursor);
    const output = formatOutput({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } }, 'cursor');
    assert.ok(output);
  });

  test('Codex round-trip: normalize → formatOutput, model+turn_id preserved', () => {
    const normalized = normalize(fxCodex);
    const output = formatOutput({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } }, 'codex');
    assert.equal(normalized.model, fxCodex.model);
    assert.equal(normalized.turn_id, fxCodex.turn_id);
    assert.ok(output.hookSpecificOutput);
  });

  // 🔴 RED until real Windsurf fixture captured
  test('Windsurf round-trip', { todo: 'Requires real Windsurf capture' }, () => {
    const normalized = normalize(fxWindsurf);
    const output = formatOutput({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } }, 'windsurf');
    assert.ok(output);
  });

  // 🔴 RED until real Copilot fixture captured
  test('Copilot round-trip', { todo: 'Requires real Copilot capture' }, () => {
    const normalized = normalize(fxCopilot);
    const output = formatOutput({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } }, 'copilot');
    assert.ok(output);
  });

});
