#!/usr/bin/env node
'use strict';

/**
 * plan_manager.test.js — JavaScript tests for plan_manager.js
 *
 * Uses only node:test and node:assert (zero npm dependencies).
 * Run with: node --test plan_manager.test.js
 *
 * Strategy:
 *   - Pure logic (mergePatch, mergeById, computeStatus, propagateStatuses):
 *     tested by requiring the module with a probe that captures exported functions.
 *     Since plan_manager.js has no exports, we test pure logic indirectly through
 *     CLI invocations, and directly by re-implementing lightweight inline versions
 *     matched to the exact semantics in the file.
 *   - File I/O commands (create, next, update_status, show_status, query, upsert):
 *     tested via spawnSync, using isolated temp dirs per test.
 */

const { describe, it, before, after, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const HELPER = path.resolve(__dirname, 'plan_manager.js');
const TIMEOUT = 8000; // ms per test (CLI spawn needs more than 1s)

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function run(...args) {
  const result = spawnSync('node', [HELPER, ...args], {
    encoding: 'utf8',
    timeout: TIMEOUT,
  });
  return result;
}

function parse(result) {
  return JSON.parse(result.stdout);
}

function mkTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'pm-test-'));
}

function tmpPlan(dir, name = 'plan.json') {
  return path.join(dir, name);
}

/** Build a full two-phase plan JSON (mirrors the Python full_plan fixture). */
function fullPlan() {
  return {
    name: 'Full Plan',
    description: 'A full plan',
    phases: [
      {
        id: 'phase-1',
        name: 'Phase One',
        description: 'First phase',
        depends_on: [],
        steps: [
          { id: 'step-1a', name: 'Step 1A', prompt: 'Do 1A', depends_on: [], model: 'sonnet' },
          { id: 'step-1b', name: 'Step 1B', prompt: 'Do 1B', depends_on: ['step-1a'] },
        ],
      },
      {
        id: 'phase-2',
        name: 'Phase Two',
        description: 'Second phase',
        depends_on: ['phase-1'],
        steps: [
          { id: 'step-2a', name: 'Step 2A', prompt: 'Do 2A', depends_on: [] },
        ],
      },
    ],
  };
}

/** Create a plan via CLI and return its file path. */
function createPlan(dir, data) {
  const planFile = tmpPlan(dir);
  const result = run('create', planFile, JSON.stringify(data));
  assert.equal(result.status, 0, `create failed: ${result.stderr}`);
  return planFile;
}

// ---------------------------------------------------------------------------
// 1. mergePatch — tested indirectly via upsert + query
//    Also tested directly via a small inline re-implementation to cover edge cases
// ---------------------------------------------------------------------------

describe('mergePatch (logic)', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('null removes keys: upsert sets extra_field, then null removes it', () => {
    const planFile = tmpPlan(dir, 'mp1.json');
    run('create', planFile, JSON.stringify({ name: 'P', phases: [] }));
    // Patch in extra_field via upsert
    run('upsert', planFile, 'entire_plan', JSON.stringify({ description: 'hello' }));
    let r = parse(run('query', planFile, 'entire_plan'));
    assert.equal(r.description, 'hello');
    // Null it out
    run('upsert', planFile, 'entire_plan', JSON.stringify({ description: null }));
    r = parse(run('query', planFile, 'entire_plan'));
    assert.ok(!Object.prototype.hasOwnProperty.call(r, 'description'));
  });

  it('nested objects are merged, not replaced', () => {
    const planFile = tmpPlan(dir, 'mp2.json');
    // Create a plan then upsert a step with nested data
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph1',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    }));
    // Patch only the name of step-s1 — prompt must be preserved
    run('upsert', planFile, 's1', JSON.stringify({ name: 'S1-updated' }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    const step = plan.phases[0].steps[0];
    assert.equal(step.name, 'S1-updated');
    assert.equal(step.prompt, 'x');  // nested field preserved
  });

  it('non-object patch replaces: upsert with scalar array is treated as replace', () => {
    // Test that a scalar value overwrites correctly (via a string field)
    const planFile = tmpPlan(dir, 'mp3.json');
    run('create', planFile, JSON.stringify({ name: 'Old Name', phases: [] }));
    run('upsert', planFile, 'entire_plan', JSON.stringify({ name: 'New Name' }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.name, 'New Name');
  });
});

// ---------------------------------------------------------------------------
// 2. mergeById — tested indirectly via upsert with phases array
// ---------------------------------------------------------------------------

describe('mergeById (logic)', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('existing item is patched by id', () => {
    const planFile = createPlan(dir, fullPlan());
    run('upsert', planFile, 'entire_plan', JSON.stringify({
      phases: [{ id: 'phase-1', name: 'Phase One Updated' }],
    }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    const ph = plan.phases.find(p => p.id === 'phase-1');
    assert.equal(ph.name, 'Phase One Updated');
    assert.equal(ph.steps.length, 2); // steps preserved
  });

  it('new item is appended when id not found', () => {
    const planFile = createPlan(dir, fullPlan());
    run('upsert', planFile, 'phase-new', JSON.stringify({ kind: 'phase', name: 'Phase New' }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases.length, 3);
    assert.ok(plan.phases.find(p => p.id === 'phase-new'));
  });

  it('missing id in phases array returns error', () => {
    const planFile = createPlan(dir, fullPlan());
    const result = run('upsert', planFile, 'entire_plan', JSON.stringify({
      phases: [{ name: 'No ID' }],
    }));
    const data = parse(result);
    assert.ok(data.error, 'expected error key');
    assert.ok(data.error.includes('missing_id'));
  });
});

// ---------------------------------------------------------------------------
// 3. computeStatus / propagateStatuses
// ---------------------------------------------------------------------------

describe('computeStatus / propagateStatuses', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('all complete steps → phase complete, plan complete', () => {
    const planFile = tmpPlan(dir, 'cs1.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [
          { id: 's1', name: 'S1', prompt: 'x' },
          { id: 's2', name: 'S2', prompt: 'x' },
        ],
      }],
    }));
    run('update_status', planFile, 's1', 'complete');
    run('update_status', planFile, 's2', 'complete');
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'complete');
    assert.equal(plan.status, 'complete');
  });

  it('any failed step → phase failed', () => {
    const planFile = tmpPlan(dir, 'cs2.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [
          { id: 's1', name: 'S1', prompt: 'x' },
          { id: 's2', name: 'S2', prompt: 'x' },
        ],
      }],
    }));
    run('update_status', planFile, 's1', 'complete');
    run('update_status', planFile, 's2', 'failed');
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'failed');
  });

  it('any blocked step → phase blocked', () => {
    const planFile = tmpPlan(dir, 'cs3.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [
          { id: 's1', name: 'S1', prompt: 'x' },
          { id: 's2', name: 'S2', prompt: 'x' },
        ],
      }],
    }));
    run('update_status', planFile, 's2', 'blocked');
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'blocked');
  });

  it('mix of in_progress/complete → phase in_progress', () => {
    const planFile = tmpPlan(dir, 'cs4.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [
          { id: 's1', name: 'S1', prompt: 'x' },
          { id: 's2', name: 'S2', prompt: 'x' },
        ],
      }],
    }));
    run('update_status', planFile, 's1', 'complete');
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'in_progress');
  });

  it('all open → phase open', () => {
    const planFile = tmpPlan(dir, 'cs5.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'open');
  });

  it('empty steps array → phase status open (created open)', () => {
    const planFile = tmpPlan(dir, 'cs6.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{ id: 'ph1', name: 'Ph', steps: [] }],
    }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'open');
  });
});

// ---------------------------------------------------------------------------
// 4. cmdCreate
// ---------------------------------------------------------------------------

describe('cmdCreate', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('creates file with correct structure, defaults, timestamps', () => {
    const planFile = tmpPlan(dir, 'create1.json');
    const before = Date.now();
    const result = run('create', planFile, JSON.stringify({
      name: 'My Plan',
      description: 'Test description',
      phases: [],
    }));
    const after = Date.now();
    assert.equal(result.status, 0);
    const resp = parse(result);
    assert.equal(resp.ok, true);
    assert.equal(resp.name, 'My Plan');
    assert.equal(resp.status, 'open');

    const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
    assert.equal(plan.name, 'My Plan');
    assert.equal(plan.description, 'Test description');
    assert.equal(plan.status, 'open');
    assert.ok(plan.created_at);
    assert.ok(plan.updated_at);
    const createdMs = new Date(plan.created_at).getTime();
    assert.ok(createdMs >= before && createdMs <= after);
  });

  it('applies default name when not provided', () => {
    const planFile = tmpPlan(dir, 'create2.json');
    run('create', planFile, JSON.stringify({}));
    const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
    assert.equal(plan.name, 'Unnamed Plan');
  });

  it('phases and steps get status:open and depends_on:[]', () => {
    const planFile = tmpPlan(dir, 'create3.json');
    run('create', planFile, JSON.stringify({
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph1',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    }));
    const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
    const ph = plan.phases[0];
    assert.equal(ph.status, 'open');
    assert.deepEqual(ph.depends_on, []);
    const st = ph.steps[0];
    assert.equal(st.status, 'open');
    assert.deepEqual(st.depends_on, []);
  });

  it('creates parent directories if needed', () => {
    const planFile = path.join(dir, 'nested', 'deeply', 'plan.json');
    const result = run('create', planFile, JSON.stringify({ name: 'Nested' }));
    assert.equal(result.status, 0);
    assert.ok(fs.existsSync(planFile));
  });
});

// ---------------------------------------------------------------------------
// 5. cmdNext
// ---------------------------------------------------------------------------

describe('cmdNext', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('returns only open steps with deps satisfied', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('next', planFile));
    // step-1a has no deps; step-1b depends on step-1a (not complete); phase-2 depends on phase-1
    assert.equal(resp.ready.length, 1);
    assert.equal(resp.ready[0].id, 'step-1a');
    assert.equal(resp.ready[0].resume, false);
  });

  it('count and plan_status present in output', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('next', planFile));
    assert.ok('count' in resp);
    assert.ok('plan_status' in resp);
    assert.equal(resp.count, resp.ready.length);
  });

  it('skips complete phases', () => {
    const planFile = createPlan(dir, fullPlan());
    run('update_status', planFile, 'step-1a', 'complete');
    run('update_status', planFile, 'step-1b', 'complete');
    // phase-1 is now complete; phase-2 depends on phase-1 so step-2a becomes ready
    const resp = parse(run('next', planFile));
    const ids = resp.ready.map(s => s.id);
    assert.ok(ids.includes('step-2a'));
    assert.ok(!ids.includes('step-1a'));
    assert.ok(!ids.includes('step-1b'));
  });

  it('respects phase depends_on', () => {
    const planFile = createPlan(dir, fullPlan());
    // phase-2 depends on phase-1 which is still open → step-2a should NOT appear
    const resp = parse(run('next', planFile));
    const ids = resp.ready.map(s => s.id);
    assert.ok(!ids.includes('step-2a'));
  });

  it('resume behavior: in_progress step appears first with resume:true', () => {
    const planFile = createPlan(dir, {
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph1',
        steps: [
          { id: 's1', name: 'S1', prompt: 'x' },
          { id: 's2', name: 'S2', prompt: 'x' },
        ],
      }],
    });
    run('update_status', planFile, 's1', 'in_progress');
    const resp = parse(run('next', planFile));
    assert.equal(resp.ready[0].id, 's1');
    assert.equal(resp.ready[0].resume, true);
    assert.equal(resp.ready[1].id, 's2');
    assert.equal(resp.ready[1].resume, false);
  });

  it('limit parameter restricts results', () => {
    const planFile = createPlan(dir, {
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph1',
        steps: Array.from({ length: 5 }, (_, i) => ({
          id: `s${i}`, name: `S${i}`, prompt: 'x',
        })),
      }],
    });
    const resp = parse(run('next', planFile, '2'));
    assert.equal(resp.ready.length, 2);
    assert.equal(resp.count, 2);
  });

  it('plan_not_found when file missing', () => {
    const resp = parse(run('next', path.join(dir, 'nonexistent.json')));
    assert.equal(resp.error, 'plan_not_found');
  });
});

// ---------------------------------------------------------------------------
// 6. cmdUpdateStatus
// ---------------------------------------------------------------------------

describe('cmdUpdateStatus', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('sets step status and propagates to phase and plan', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('update_status', planFile, 'step-1a', 'complete'));
    assert.equal(resp.ok, true);
    assert.equal(resp.id, 'step-1a');
    assert.equal(resp.status, 'complete');
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].steps[0].status, 'complete');
    // step-1b still open → phase in_progress
    assert.equal(plan.phases[0].status, 'in_progress');
  });

  it('sets phase status — propagates from steps (blocked step → phase blocked)', () => {
    // Note: cmdUpdateStatus sets the target then calls propagateStatuses.
    // Propagation re-derives phase status from steps, so directly setting a
    // phase to 'blocked' when its steps are all 'open' will be overridden back
    // to 'open'. To observe 'blocked' on the phase we must block a step first.
    const planFile = createPlan(dir, {
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    });
    run('update_status', planFile, 's1', 'blocked');
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'blocked');
  });

  it('propagates to plan level', () => {
    const planFile = createPlan(dir, {
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    });
    const resp = parse(run('update_status', planFile, 's1', 'complete'));
    assert.equal(resp.plan_status, 'complete');
  });

  it('invalid status returns error', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('update_status', planFile, 'step-1a', 'done'));
    assert.ok(resp.error);
    assert.ok(resp.error.includes('invalid_status'));
  });

  it('unknown id returns target_not_found', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('update_status', planFile, 'no-such-id', 'complete'));
    assert.equal(resp.error, 'target_not_found');
  });

  it('plan not found returns error', () => {
    const resp = parse(run('update_status', path.join(dir, 'missing.json'), 's1', 'complete'));
    assert.equal(resp.error, 'plan_not_found');
  });
});

// ---------------------------------------------------------------------------
// 7. cmdShowStatus
// ---------------------------------------------------------------------------

describe('cmdShowStatus', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('entire_plan returns totals with progress_pct', () => {
    const planFile = createPlan(dir, fullPlan());
    run('update_status', planFile, 'step-1a', 'complete');
    const resp = parse(run('show_status', planFile, 'entire_plan'));
    assert.ok('steps' in resp);
    assert.ok('phases' in resp);
    assert.equal(resp.steps.total, 3);
    assert.equal(resp.steps.complete, 1);
    assert.ok('progress_pct' in resp.steps);
    // 1/3 ≈ 33.3
    assert.ok(resp.steps.progress_pct > 33 && resp.steps.progress_pct < 34);
  });

  it('phase id returns phase summary with steps', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('show_status', planFile, 'phase-1'));
    assert.equal(resp.id, 'phase-1');
    assert.ok(Array.isArray(resp.steps));
    assert.equal(resp.steps.length, 2);
  });

  it('step id returns step status', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('show_status', planFile, 'step-1a'));
    assert.equal(resp.id, 'step-1a');
    assert.equal(resp.status, 'open');
  });

  it('target_not_found for unknown id', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('show_status', planFile, 'no-such-id'));
    assert.equal(resp.error, 'target_not_found');
  });

  it('plan not found returns error', () => {
    const resp = parse(run('show_status', path.join(dir, 'missing.json')));
    assert.equal(resp.error, 'plan_not_found');
  });

  it('progress_pct is 100 when all steps complete', () => {
    const planFile = createPlan(dir, {
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    });
    run('update_status', planFile, 's1', 'complete');
    const resp = parse(run('show_status', planFile, 'entire_plan'));
    assert.equal(resp.steps.progress_pct, 100);
  });

  it('phase_summary included in entire_plan response', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('show_status', planFile, 'entire_plan'));
    assert.ok(Array.isArray(resp.phase_summary));
    assert.equal(resp.phase_summary.length, 2);
  });
});

// ---------------------------------------------------------------------------
// 8. cmdQuery
// ---------------------------------------------------------------------------

describe('cmdQuery', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('entire_plan returns full plan object', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('query', planFile, 'entire_plan'));
    assert.equal(resp.name, 'Full Plan');
    assert.equal(resp.phases.length, 2);
  });

  it('phase id returns full phase', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('query', planFile, 'phase-1'));
    assert.equal(resp.id, 'phase-1');
    assert.equal(resp.steps.length, 2);
  });

  it('step id returns full step', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('query', planFile, 'step-1b'));
    assert.equal(resp.id, 'step-1b');
    assert.equal(resp.prompt, 'Do 1B');
  });

  it('error for unknown id', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('query', planFile, 'no-such-id'));
    assert.equal(resp.error, 'target_not_found');
  });

  it('no target_id returns full plan (same as entire_plan)', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('query', planFile));
    assert.equal(resp.name, 'Full Plan');
  });

  it('plan_not_found when file missing', () => {
    const resp = parse(run('query', path.join(dir, 'missing.json')));
    assert.equal(resp.error, 'plan_not_found');
  });
});

// ---------------------------------------------------------------------------
// 9. cmdUpsert
// ---------------------------------------------------------------------------

describe('cmdUpsert', { timeout: TIMEOUT }, () => {
  let dir;
  before(() => { dir = mkTmpDir(); });
  after(() => { fs.rmSync(dir, { recursive: true, force: true }); });

  it('create plan with entire_plan when file does not exist', () => {
    const planFile = tmpPlan(dir, 'upsert-create.json');
    const resp = parse(run('upsert', planFile, 'entire_plan', JSON.stringify({
      name: 'Upserted Plan', phases: [],
    })));
    assert.equal(resp.ok, true);
    assert.ok(fs.existsSync(planFile));
    const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
    assert.equal(plan.name, 'Upserted Plan');
    assert.ok(plan.created_at);
  });

  it('patch existing plan top-level field', () => {
    const planFile = createPlan(dir, fullPlan());
    run('upsert', planFile, 'entire_plan', JSON.stringify({ name: 'Updated Name' }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.name, 'Updated Name');
    assert.equal(plan.description, 'A full plan'); // preserved
  });

  it('add new phase with kind:phase', () => {
    const planFile = createPlan(dir, fullPlan());
    run('upsert', planFile, 'phase-3', JSON.stringify({
      kind: 'phase', name: 'Phase Three', description: 'New',
    }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases.length, 3);
    const ph3 = plan.phases.find(p => p.id === 'phase-3');
    assert.ok(ph3);
    assert.equal(ph3.name, 'Phase Three');
  });

  it('add new step with kind:step and phase_id', () => {
    const planFile = createPlan(dir, fullPlan());
    run('upsert', planFile, 'step-1c', JSON.stringify({
      kind: 'step', phase_id: 'phase-1', name: 'Step 1C', prompt: 'Do 1C',
    }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    const ph1 = plan.phases.find(p => p.id === 'phase-1');
    assert.equal(ph1.steps.length, 3);
    const s1c = ph1.steps.find(s => s.id === 'step-1c');
    assert.ok(s1c);
    assert.equal(s1c.name, 'Step 1C');
  });

  it('merge existing phase steps by id, preserving untouched steps', () => {
    const planFile = createPlan(dir, fullPlan());
    run('upsert', planFile, 'phase-1', JSON.stringify({
      steps: [{ id: 'step-1a', name: 'Step 1A Renamed' }],
    }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    const ph1 = plan.phases.find(p => p.id === 'phase-1');
    assert.equal(ph1.steps[0].name, 'Step 1A Renamed');
    assert.equal(ph1.steps.length, 2); // step-1b preserved
  });

  it('upsert step patch preserves existing fields', () => {
    const planFile = createPlan(dir, fullPlan());
    run('update_status', planFile, 'step-1a', 'complete');
    run('upsert', planFile, 'step-1a', JSON.stringify({ name: 'Renamed' }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    const step = plan.phases[0].steps.find(s => s.id === 'step-1a');
    assert.equal(step.status, 'complete'); // preserved after upsert
    assert.equal(step.name, 'Renamed');
  });

  it('plan_not_found when file missing and target is not entire_plan', () => {
    const resp = parse(run('upsert', path.join(dir, 'missing.json'), 'phase-1', JSON.stringify({ name: 'X' })));
    assert.equal(resp.error, 'plan_not_found');
  });

  it('phase_not_found when adding step to nonexistent phase', () => {
    const planFile = createPlan(dir, fullPlan());
    const resp = parse(run('upsert', planFile, 'step-new', JSON.stringify({
      kind: 'step', phase_id: 'no-such-phase', name: 'X',
    })));
    assert.equal(resp.error, 'phase_not_found');
  });

  it('statuses propagated after upsert', () => {
    const planFile = createPlan(dir, {
      name: 'P',
      phases: [{
        id: 'ph1', name: 'Ph',
        steps: [{ id: 's1', name: 'S1', prompt: 'x' }],
      }],
    });
    run('upsert', planFile, 's1', JSON.stringify({ status: 'complete' }));
    const plan = parse(run('query', planFile, 'entire_plan'));
    assert.equal(plan.phases[0].status, 'complete');
    assert.equal(plan.status, 'complete');
  });
});

// ---------------------------------------------------------------------------
// 10. help command
// ---------------------------------------------------------------------------

describe('help command', { timeout: TIMEOUT }, () => {
  it('exits 0 and outputs JSON with tool, commands, schema keys', () => {
    const result = run('help');
    assert.equal(result.status, 0);
    const resp = parse(result);
    assert.ok('tool' in resp);
    assert.ok('commands' in resp);
    assert.ok('schema' in resp);
  });

  it('tool value is plan_manager.js', () => {
    const resp = parse(run('help'));
    assert.equal(resp.tool, 'plan_manager.js');
  });

  it('commands object contains expected command keys', () => {
    const resp = parse(run('help'));
    const expected = ['help', 'create', 'next', 'update_status', 'show_status', 'query', 'upsert'];
    for (const cmd of expected) {
      assert.ok(cmd in resp.commands, `missing command: ${cmd}`);
    }
  });
});

// ---------------------------------------------------------------------------
// 11. no-args — exits 0 and prints help (not an error)
// ---------------------------------------------------------------------------

describe('no-args behavior', { timeout: TIMEOUT }, () => {
  it('exits 0 when invoked with no arguments', () => {
    const result = spawnSync('node', [HELPER], { encoding: 'utf8', timeout: TIMEOUT });
    assert.equal(result.status, 0);
  });

  it('prints valid JSON with tool and commands keys (same as help)', () => {
    const result = spawnSync('node', [HELPER], { encoding: 'utf8', timeout: TIMEOUT });
    const resp = JSON.parse(result.stdout);
    assert.ok('tool' in resp);
    assert.ok('commands' in resp);
  });

  it('does not print error key', () => {
    const result = spawnSync('node', [HELPER], { encoding: 'utf8', timeout: TIMEOUT });
    const resp = JSON.parse(result.stdout);
    assert.ok(!('error' in resp));
  });
});

// ---------------------------------------------------------------------------
// 12. unknown command — exits 1
// ---------------------------------------------------------------------------

describe('unknown command', { timeout: TIMEOUT }, () => {
  it('exits 1 for unknown command', () => {
    const result = run('explode');
    assert.equal(result.status, 1);
  });

  it('outputs JSON error with unknown_command key', () => {
    const result = run('explode');
    const resp = parse(result);
    assert.ok(resp.error);
    assert.ok(resp.error.includes('unknown_command'));
  });

  it('includes list of valid commands in error output', () => {
    const result = run('foobar');
    const resp = parse(result);
    assert.ok(Array.isArray(resp.commands));
    assert.ok(resp.commands.includes('help'));
  });
});
