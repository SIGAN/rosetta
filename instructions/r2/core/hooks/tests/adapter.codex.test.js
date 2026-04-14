'use strict';
// adapter.codex.test.js — Tests for Codex IDE adapter
// Run: node --test instructions/r2/core/hooks/tests/adapter.codex.test.js

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');

const FIXTURES = path.join(__dirname, 'fixtures');
const fx = (name) => require(path.join(FIXTURES, name));

const fxCodexBash  = fx('codex-post-tool-use-bash.json');

const { detectIDE, normalize, formatOutput } = require('../adapter');

// ---------------------------------------------------------------------------
describe('detectIDE — Codex', () => {

  test('returns "codex" for Codex PostToolUse Bash input', () => {
    assert.equal(detectIDE(fxCodexBash), 'codex');
  });

});

// ---------------------------------------------------------------------------
describe('normalize — Codex', () => {

  test('identity pass-through, preserves model + turn_id', () => {
    const result = normalize(fxCodexBash);
    assert.ok(result.hook_event_name, 'hook_event_name missing');
    assert.ok(result.tool_name, 'tool_name missing');
    assert.ok(result.tool_input, 'tool_input missing');
    assert.equal(result.model, fxCodexBash.model, 'model not preserved');
    assert.equal(result.turn_id, fxCodexBash.turn_id, 'turn_id not preserved');
  });

});

// ---------------------------------------------------------------------------
describe('formatOutput — Codex', () => {

  test('identity pass-through (same schema as Claude Code)', () => {
    const canonical = { hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } };
    const result = formatOutput(canonical, 'codex');
    assert.deepEqual(result, canonical);
  });

});

// ---------------------------------------------------------------------------
describe('round-trip — Codex', () => {

  test('normalize → formatOutput, model+turn_id preserved', () => {
    const normalized = normalize(fxCodexBash);
    const output = formatOutput({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: 'x' } }, 'codex');
    assert.equal(normalized.model, fxCodexBash.model);
    assert.equal(normalized.turn_id, fxCodexBash.turn_id);
    assert.ok(output.hookSpecificOutput);
  });

});
