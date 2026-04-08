'use strict';
// loose-files.test.js — TDD test suite for loose-files.js
// Run: node --test instructions/r2/core/hooks/loose-files.test.js
//
// Expected results BEFORE loose-files.js exists: ALL RED (module not found)
// Expected results AFTER loose-files.js implemented: ALL GREEN

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { Readable } = require('stream');

const FIXTURES_DIR = path.join(__dirname, 'test-fixtures');
const fx = (name) => require(path.join(FIXTURES_DIR, name));

const ccWrite    = fx('claude-code-post-tool-use-write.json');
const ccEdit     = fx('claude-code-post-tool-use-edit.json');
const ccBash     = fx('claude-code-pre-tool-use-bash.json');

// loose-files.js must export testable functions:
//   shouldCheck(normalizedInput) → boolean
//   isLooseFile(filePath, mockFs) → boolean
//   buildNudgeOutput(filePath) → object
const { shouldCheck, isLooseFile, buildNudgeOutput } = require('./loose-files');

// ---------------------------------------------------------------------------
// Mock filesystem factory
// existingPaths: array of absolute paths that "exist"
function mockFs(existingPaths) {
  return {
    existsSync: (p) => existingPaths.includes(p)
  };
}

// ---------------------------------------------------------------------------
describe('shouldCheck — file extension filter', () => {

  test('.py file → true', () => {
    const input = { ...ccWrite, tool_input: { file_path: '/proj/utils.py' } };
    assert.equal(shouldCheck(input), true);
  });

  test('.js file → true', () => {
    const input = { ...ccWrite, tool_input: { file_path: '/proj/app.js' } };
    assert.equal(shouldCheck(input), true);
  });

  test('.ts file → false', () => {
    const input = { ...ccWrite, tool_input: { file_path: '/proj/app.ts' } };
    assert.equal(shouldCheck(input), false);
  });

  test('.md file → false', () => {
    const input = { ...ccWrite, tool_input: { file_path: '/proj/README.md' } };
    assert.equal(shouldCheck(input), false);
  });

  test('.json file → false', () => {
    const input = { ...ccWrite, tool_input: { file_path: '/proj/config.json' } };
    assert.equal(shouldCheck(input), false);
  });

});

// ---------------------------------------------------------------------------
describe('shouldCheck — event + tool filter', () => {

  test('PostToolUse + Write → true', () => {
    assert.equal(shouldCheck(ccWrite), true);
  });

  test('PostToolUse + Edit → true', () => {
    assert.equal(shouldCheck(ccEdit), true);
  });

  test('PostToolUse + Bash → false', () => {
    assert.equal(shouldCheck(ccBash), false);
  });

  test('PostToolUse + Read → false', () => {
    const input = { ...ccWrite, tool_name: 'Read' };
    assert.equal(shouldCheck(input), false);
  });

  test('PreToolUse + Write → false (wrong event)', () => {
    const input = { ...ccWrite, hook_event_name: 'PreToolUse' };
    assert.equal(shouldCheck(input), false);
  });

});

// ---------------------------------------------------------------------------
describe('shouldCheck — exclusion paths', () => {

  const makeInput = (filePath) => ({
    ...ccWrite,
    tool_input: { file_path: filePath }
  });

  test('path contains agents/TEMP/ → false', () => {
    assert.equal(shouldCheck(makeInput('/proj/agents/TEMP/debug.py')), false);
  });

  test('path contains scripts/ → false', () => {
    assert.equal(shouldCheck(makeInput('/proj/scripts/runner.py')), false);
  });

  test('path contains node_modules/ → false', () => {
    assert.equal(shouldCheck(makeInput('/proj/node_modules/foo/bar.js')), false);
  });

  test('path contains .venv/ → false', () => {
    assert.equal(shouldCheck(makeInput('/proj/.venv/lib/site.py')), false);
  });

  test('path contains __pycache__/ → false', () => {
    assert.equal(shouldCheck(makeInput('/proj/src/__pycache__/util.py')), false);
  });

});

// ---------------------------------------------------------------------------
describe('isLooseFile — Python module detection (.py)', () => {

  test('.py with __init__.py in same dir → false (not loose)', () => {
    const filePath = '/proj/src/mypackage/utils.py';
    const fs = mockFs(['/proj/src/mypackage/__init__.py']);
    assert.equal(isLooseFile(filePath, fs), false);
  });

  test('.py with __init__.py two levels up → false', () => {
    const filePath = '/proj/src/mypackage/sub/utils.py';
    const fs = mockFs(['/proj/src/mypackage/__init__.py']);
    assert.equal(isLooseFile(filePath, fs), false);
  });

  test('.py with NO __init__.py anywhere → true (loose)', () => {
    const filePath = '/proj/orphan.py';
    const fs = mockFs([]);
    assert.equal(isLooseFile(filePath, fs), true);
  });

  test('.py at root with no markers — stops at 10 levels max, returns true', () => {
    const filePath = '/a/b/c/d/e/f/g/h/i/j/k/deep.py';
    const fs = mockFs([]);
    assert.equal(isLooseFile(filePath, fs), true);
  });

});

// ---------------------------------------------------------------------------
describe('isLooseFile — JavaScript module detection (.js)', () => {

  test('.js with package.json in same dir → false (not loose)', () => {
    const filePath = '/proj/src/app.js';
    const fs = mockFs(['/proj/src/package.json']);
    assert.equal(isLooseFile(filePath, fs), false);
  });

  test('.js with package.json three levels up → false', () => {
    const filePath = '/proj/src/lib/utils/helpers.js';
    const fs = mockFs(['/proj/src/package.json']);
    assert.equal(isLooseFile(filePath, fs), false);
  });

  test('.js with NO package.json anywhere → true (loose)', () => {
    const filePath = '/proj/helper.js';
    const fs = mockFs([]);
    assert.equal(isLooseFile(filePath, fs), true);
  });

  test('.js at deep nesting — stops at 10 levels, returns true', () => {
    const filePath = '/a/b/c/d/e/f/g/h/i/j/k/deep.js';
    const fs = mockFs([]);
    assert.equal(isLooseFile(filePath, fs), true);
  });

});

// ---------------------------------------------------------------------------
describe('buildNudgeOutput', () => {

  test('returns valid JSON-serializable object', () => {
    const result = buildNudgeOutput('/proj/orphan.py');
    const serialized = JSON.stringify(result);
    assert.ok(serialized, 'result is not JSON serializable');
    JSON.parse(serialized); // must not throw
  });

  test('has hookSpecificOutput.hookEventName === "PostToolUse"', () => {
    const result = buildNudgeOutput('/proj/orphan.py');
    assert.equal(result.hookSpecificOutput.hookEventName, 'PostToolUse');
  });

  test('.py — additionalContext mentions file path', () => {
    const result = buildNudgeOutput('/proj/orphan.py');
    assert.ok(result.hookSpecificOutput.additionalContext.includes('orphan.py'));
  });

  test('.py — additionalContext mentions __init__.py', () => {
    const result = buildNudgeOutput('/proj/orphan.py');
    assert.ok(result.hookSpecificOutput.additionalContext.includes('__init__.py'));
  });

  test('.js — additionalContext mentions package.json', () => {
    const result = buildNudgeOutput('/proj/helper.js');
    assert.ok(result.hookSpecificOutput.additionalContext.includes('package.json'));
  });

  test('has continue: true', () => {
    const result = buildNudgeOutput('/proj/orphan.py');
    assert.equal(result.continue, true);
  });

});

// ---------------------------------------------------------------------------
describe('integration with adapter', () => {

  const { normalize } = require('./adapter');

  test('Claude Code Write fixture (.py loose) → shouldCheck=true + isLooseFile=true', () => {
    const input = {
      ...ccWrite,
      tool_input: { file_path: '/proj/orphan.py', content: 'pass\n' },
      tool_response: { filePath: '/proj/orphan.py' }
    };
    const normalized = normalize(input);
    assert.equal(shouldCheck(normalized), true);
    const fs = mockFs([]);
    assert.equal(isLooseFile(normalized.tool_input.file_path, fs), true);
  });

  test('Claude Code Write fixture (.py inside module) → shouldCheck=true + isLooseFile=false', () => {
    const input = {
      ...ccWrite,
      tool_input: { file_path: '/proj/src/mypackage/utils.py', content: 'pass\n' },
      tool_response: { filePath: '/proj/src/mypackage/utils.py' }
    };
    const normalized = normalize(input);
    assert.equal(shouldCheck(normalized), true);
    const fs = mockFs(['/proj/src/mypackage/__init__.py']);
    assert.equal(isLooseFile(normalized.tool_input.file_path, fs), false);
  });

  test('Claude Code Edit fixture (.js loose) → shouldCheck=true + isLooseFile=true', () => {
    const normalized = normalize(ccEdit);
    // ccEdit file_path is /proj/src/app.js — no package.json in mockFs
    assert.equal(shouldCheck(normalized), true);
    const fs = mockFs([]);
    assert.equal(isLooseFile(normalized.tool_input.file_path, fs), true);
  });

  test('Claude Code Bash fixture → shouldCheck=false', () => {
    const normalized = normalize(ccBash);
    assert.equal(shouldCheck(normalized), false);
  });

});
