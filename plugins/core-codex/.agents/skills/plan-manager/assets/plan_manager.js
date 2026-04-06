#!/usr/bin/env node
'use strict';

/**
 * plan_manager.js — plan manager for coding agents.
 * Plans are stored as JSON files with two levels: phases contain steps.
 * Status propagates bottom-up: steps → phases → plan.
 *
 * Usage: node plan_manager.js <cmd> <plan-file> [args...]
 *
 * Commands:
 *   create        <plan-file> '<plan-json>'
 *   next          <plan-file> [limit=10]
 *   update_status <plan-file> <id> <status>
 *   show_status   <plan-file> [id|entire_plan]
 *   query         <plan-file> [id|entire_plan]
 *   upsert        <plan-file> <target-id> '<patch-json>'
 */

const fs   = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// RFC 7396 Merge Patch
// ---------------------------------------------------------------------------

function mergePatch(target, patch) {
  if (typeof patch !== 'object' || patch === null || Array.isArray(patch)) return patch;
  if (typeof target !== 'object' || target === null || Array.isArray(target)) target = {};
  const result = Object.assign({}, target);
  for (const [key, value] of Object.entries(patch)) {
    if (value === null) delete result[key];
    else result[key] = mergePatch(result[key], value);
  }
  return result;
}

function mergeById(existing, incoming) {
  const result = [...existing];
  for (const patch of incoming) {
    if (!patch.id) return { error: 'missing_id' };
    const idx = result.findIndex(i => i.id === patch.id);
    if (idx >= 0) result[idx] = mergePatch(result[idx], patch);
    else result.push(Object.assign({}, patch));
  }
  return result;
}

// ---------------------------------------------------------------------------
// Status helpers
// ---------------------------------------------------------------------------

function computeStatus(statuses) {
  if (!statuses.length) return 'open';
  if (statuses.every(s => s === 'complete')) return 'complete';
  if (statuses.some(s => s === 'failed')) return 'failed';
  if (statuses.some(s => s === 'blocked')) return 'blocked';
  if (statuses.some(s => s === 'in_progress' || s === 'complete')) return 'in_progress';
  return 'open';
}

function propagateStatuses(plan) {
  for (const phase of plan.phases || []) {
    const ss = (phase.steps || []).map(s => s.status || 'open');
    if (ss.length) phase.status = computeStatus(ss);
  }
  const ps = (plan.phases || []).map(p => p.status || 'open');
  if (ps.length) plan.status = computeStatus(ps);
}

// ---------------------------------------------------------------------------
// Dependency helpers
// ---------------------------------------------------------------------------

function buildStatusMap(plan) {
  const m = {};
  for (const phase of plan.phases || []) {
    if (phase.id) m[phase.id] = phase.status || 'open';
    for (const step of phase.steps || [])
      if (step.id) m[step.id] = step.status || 'open';
  }
  return m;
}

function depsSatisfied(item, map) {
  return (item.depends_on || []).every(d => map[d] === 'complete');
}

// ---------------------------------------------------------------------------
// File I/O
// ---------------------------------------------------------------------------

function loadPlan(file) {
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function savePlan(file, plan) {
  const dir = path.dirname(file);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  plan.updated_at = new Date().toISOString();
  fs.writeFileSync(file, JSON.stringify(plan, null, 2));
}

function out(data) {
  console.log(JSON.stringify(data, null, 2));
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

function cmdCreate(planFile, data) {
  const now = new Date().toISOString();
  const plan = {
    name: data.name || 'Unnamed Plan',
    description: data.description || '',
    status: 'open',
    created_at: now,
    updated_at: now,
    phases: (data.phases || []).map(p => ({
      status: 'open',
      depends_on: [],
      steps: [],
      ...p,
      steps: (p.steps || []).map(s => ({ status: 'open', depends_on: [], ...s })),
    })),
  };
  propagateStatuses(plan);
  savePlan(planFile, plan);
  out({ ok: true, plan_file: planFile, name: plan.name, status: plan.status });
}

function cmdNext(planFile, limit) {
  const plan = loadPlan(planFile);
  if (!plan) return out({ error: 'plan_not_found' });
  const map = buildStatusMap(plan);
  const inProgress = [];
  const open = [];
  for (const phase of plan.phases || []) {
    if ((phase.status || 'open') === 'complete') continue;
    if (!depsSatisfied(phase, map)) continue;
    for (const step of phase.steps || []) {
      const st = step.status || 'open';
      if (!depsSatisfied(step, map)) continue;
      if (st === 'in_progress') {
        inProgress.push({ ...step, phase_id: phase.id, phase_name: phase.name, resume: true });
      } else if (st === 'open') {
        open.push({ ...step, phase_id: phase.id, phase_name: phase.name, resume: false });
      }
    }
  }
  const ready = [...inProgress, ...open].slice(0, limit);
  out({ ready, count: ready.length, plan_status: plan.status || 'open' });
}

function cmdUpdateStatus(planFile, targetId, status) {
  const valid = ['open', 'in_progress', 'complete', 'blocked', 'failed'];
  if (!valid.includes(status)) return out({ error: `invalid_status: ${status}` });
  const plan = loadPlan(planFile);
  if (!plan) return out({ error: 'plan_not_found' });
  let found = false;
  for (const phase of plan.phases || []) {
    if (phase.id === targetId) { phase.status = status; found = true; break; }
    for (const step of phase.steps || []) {
      if (step.id === targetId) { step.status = status; found = true; break; }
    }
    if (found) break;
  }
  if (!found) return out({ error: 'target_not_found' });
  propagateStatuses(plan);
  savePlan(planFile, plan);
  out({ ok: true, id: targetId, status, plan_status: plan.status });
}

function cmdShowStatus(planFile, targetId) {
  const plan = loadPlan(planFile);
  if (!plan) return out({ error: 'plan_not_found' });
  function totals(arr) {
    const t = { open: 0, in_progress: 0, complete: 0, blocked: 0, failed: 0, total: arr.length };
    arr.forEach(s => { if (s in t) t[s]++; });
    t.progress_pct = arr.length ? Math.round(t.complete / arr.length * 1000) / 10 : 0;
    return t;
  }
  if (!targetId || targetId === 'entire_plan') {
    const allStepS = (plan.phases || []).flatMap(p => (p.steps || []).map(s => s.status || 'open'));
    const phaseS   = (plan.phases || []).map(p => p.status || 'open');
    return out({
      name: plan.name,
      status: plan.status || 'open',
      phases: totals(phaseS),
      steps: totals(allStepS),
      phase_summary: (plan.phases || []).map(p => ({
        id: p.id,
        name: p.name,
        status: p.status || 'open',
        steps: (p.steps || []).map(s => ({ id: s.id, name: s.name, status: s.status || 'open' })),
      })),
    });
  }
  for (const phase of plan.phases || []) {
    if (phase.id === targetId) return out({ id: phase.id, name: phase.name, status: phase.status, steps: (phase.steps || []).map(s => ({ id: s.id, name: s.name, status: s.status })) });
    for (const step of phase.steps || [])
      if (step.id === targetId) return out({ id: step.id, name: step.name, status: step.status });
  }
  out({ error: 'target_not_found' });
}

function cmdQuery(planFile, targetId) {
  const plan = loadPlan(planFile);
  if (!plan) return out({ error: 'plan_not_found' });
  if (!targetId || targetId === 'entire_plan') return out(plan);
  for (const phase of plan.phases || []) {
    if (phase.id === targetId) return out(phase);
    for (const step of phase.steps || [])
      if (step.id === targetId) return out(step);
  }
  out({ error: 'target_not_found' });
}

function cmdUpsert(planFile, targetId, data) {
  const now = new Date().toISOString();
  let plan = loadPlan(planFile);
  if (!plan) {
    if (targetId !== 'entire_plan') return out({ error: 'plan_not_found' });
    plan = { name: 'Unnamed Plan', description: '', status: 'open', created_at: now, updated_at: now, phases: [] };
  }
  if (targetId === 'entire_plan') {
    if (data.phases && Array.isArray(data.phases)) {
      const merged = mergeById(plan.phases, data.phases);
      if (merged.error) return out(merged);
      const { phases: _p, ...rest } = data;
      plan = Object.assign({}, mergePatch(plan, rest), { phases: merged });
    } else {
      plan = mergePatch(plan, data);
    }
  } else {
    let found = false;
    for (let i = 0; i < (plan.phases || []).length; i++) {
      const phase = plan.phases[i];
      if (phase.id === targetId) {
        if (data.steps && Array.isArray(data.steps)) {
          const merged = mergeById(phase.steps || [], data.steps);
          if (merged.error) return out(merged);
          const { steps: _s, ...rest } = data;
          plan.phases[i] = Object.assign({}, mergePatch(phase, rest), { steps: merged });
        } else {
          plan.phases[i] = mergePatch(phase, data);
        }
        found = true;
        break;
      }
      for (let j = 0; j < (phase.steps || []).length; j++) {
        if (phase.steps[j].id === targetId) {
          plan.phases[i].steps[j] = mergePatch(phase.steps[j], data);
          found = true;
          break;
        }
      }
      if (found) break;
    }
    if (!found) {
      const { kind, phase_id, ...rest } = data;
      if (kind === 'step') {
        const parent = (plan.phases || []).find(p => p.id === phase_id);
        if (!parent) return out({ error: 'phase_not_found' });
        parent.steps = parent.steps || [];
        parent.steps.push({ status: 'open', depends_on: [], ...rest, id: targetId });
      } else {
        plan.phases = plan.phases || [];
        plan.phases.push({ status: 'open', depends_on: [], steps: [], name: targetId, description: '', ...rest, id: targetId });
      }
    }
  }
  propagateStatuses(plan);
  savePlan(planFile, plan);
  out({ ok: true, id: targetId, plan_status: plan.status });
}

// ---------------------------------------------------------------------------
// Help
// ---------------------------------------------------------------------------

function cmdHelp() {
  out({
    tool: 'plan_manager.js',
    description: 'Plan manager for coding agents — creates, tracks, and executes execution plans as local JSON files. No dependencies required.',
    usage: 'node plan_manager.js <cmd> <plan-file> [args...]',
    setup: {
      plugin_mode: 'If context already contains RUNNING AS A PLUGIN: plan_manager.js is at <skill_base_dir>/assets/plan_manager.js — execute directly, no copy needed',
      standard_mode: 'ACQUIRE plan-manager/assets/plan_manager.js FROM KB → save to agents/TEMP/plan_manager.js (AGENTS TEMP folder)',
    },
    plan_file: {
      convention: 'plans/<feature>/plan.json',
      note: 'Plan file lives in the FEATURE PLAN folder: plans/<feature>/',
    },
    models: {
      recommended: ['claude-sonnet-4-6', 'gpt-5.4-medium', 'gemini-3.1-pro-preview'],
      note: 'Match model to cognitive demand of plan steps',
    },
    concepts: {
      hierarchy: 'Two levels: phases contain steps. You assign string IDs.',
      statuses: 'open | in_progress | complete | blocked | failed',
      depends_on: 'Phases reference phase IDs; steps reference step IDs (cross-phase allowed).',
      status_propagation: 'Bottom-up: steps → phases → plan. all-complete=complete, any-failed=failed, any-blocked=blocked, any-in_progress/complete=in_progress, else open. Plan root status is always derived — never set manually.',
      target_id: '"entire_plan" | phase-id | step-id  (default: entire_plan)',
      resume: 'next returns in_progress steps (resume:true) before open steps (resume:false). Always check resume flag to avoid duplicate work on interrupted sessions.',
    },
    subagent_fields: {
      note: 'Available on both phases and steps for delegation',
      subagent: 'subagent name',
      role: 'specialization to assume, brilliant and short',
      model: 'comma-separated list of recommended models',
    },
    commands: {
      help: {
        usage: 'node plan_manager.js help',
        description: 'Print this documentation.',
      },
      create: {
        usage: "node plan_manager.js create plans/<feature>/plan.json '<plan-json>'",
        description: 'Create a new plan JSON file.',
        args: { 'plan-json': 'JSON with name, description?, phases[]' },
      },
      upsert: {
        usage: "node plan_manager.js upsert plans/<feature>/plan.json <target-id> '<patch-json>'",
        description: 'Create or merge-patch plan/phase/step by id. null removes a key.',
        target_id: {
          entire_plan: 'Creates plan if missing; merges phases/steps by id.',
          existing_id: 'Patches that phase or step.',
          new_id: 'Requires patch.kind="phase" or patch.kind="step" (+ patch.phase_id for steps).',
        },
      },
      query: {
        usage: 'node plan_manager.js query plans/<feature>/plan.json [target-id]',
        description: 'Return full JSON of plan, phase, or step.',
      },
      show_status: {
        usage: 'node plan_manager.js show_status plans/<feature>/plan.json [target-id]',
        description: 'Status summary with progress percentages and totals.',
      },
      update_status: {
        usage: 'node plan_manager.js update_status plans/<feature>/plan.json <id> <status>',
        description: 'Set status on a phase or step; propagates upward to plan.',
        args: { id: 'phase-id or step-id', status: 'open | in_progress | complete | blocked | failed' },
      },
      next: {
        usage: 'node plan_manager.js next plans/<feature>/plan.json [limit=10]',
        description: 'Return steps ready for execution. in_progress (resume:true) first, then open (resume:false). Loop until count:0 and plan_status:complete.',
      },
    },
    schema: {
      plan:  { name: 'str', description: 'str?', status: 'derived — never set manually, propagated from phases', phases: 'Phase[]' },
      phase: { id: 'str — unique across plan', name: 'str', description: 'str?', status: 'derived — never set manually, propagated from steps', depends_on: 'phase-id[]', subagent: 'str?', role: 'str?', model: 'str?', steps: 'Step[]' },
      step:  { id: 'str — unique across plan', name: 'str', prompt: 'str', status: 'open|in_progress|complete|blocked|failed', depends_on: 'step-id[] — cross-phase allowed', subagent: 'str?', role: 'str?', model: 'str?' },
    },
    limits: { max_phases: 100, max_steps_per_phase: 100, max_deps_per_item: 50, max_string_length: 20000, max_name_length: 256 },
    examples: [
      { label: 'Create plan',        cmd: `node plan_manager.js create plans/my-feature/plan.json '{"name":"My Feature","phases":[{"id":"p1","name":"Setup","subagent":"engineer","role":"Senior engineer","model":"claude-sonnet-4-6","steps":[{"id":"s1","name":"Init","prompt":"Initialize the project"}]}]}'` },
      { label: 'Upsert entire plan', cmd: `node plan_manager.js upsert plans/my-feature/plan.json entire_plan '{"phases":[{"id":"p2","name":"Build","steps":[{"id":"s2","name":"Compile","prompt":"Build the project"}]}]}'` },
      { label: 'Get next tasks',     cmd: 'node plan_manager.js next plans/my-feature/plan.json' },
      { label: 'Mark step done',     cmd: 'node plan_manager.js update_status plans/my-feature/plan.json s1 complete' },
      { label: 'Patch a step',       cmd: `node plan_manager.js upsert plans/my-feature/plan.json s1 '{"status":"in_progress"}'` },
      { label: 'Add new phase',      cmd: `node plan_manager.js upsert plans/my-feature/plan.json p3 '{"kind":"phase","name":"Phase 3","description":"..."}'` },
      { label: 'Add step to phase',  cmd: `node plan_manager.js upsert plans/my-feature/plan.json s3 '{"kind":"step","phase_id":"p1","name":"New Step","prompt":"Do Y"}'` },
      { label: 'Show status',        cmd: 'node plan_manager.js show_status plans/my-feature/plan.json entire_plan' },
      { label: 'Query a step',       cmd: 'node plan_manager.js query plans/my-feature/plan.json s1' },
    ],
    next_steps_for_ai: [
      '1. Setup: if context already contains RUNNING AS A PLUGIN, use <skill_base_dir>/assets/plan_manager.js directly; otherwise ACQUIRE plan-manager/assets/plan_manager.js FROM KB → save to AGENTS TEMP folder',
      '2. Create plan: node <plan_manager_full_path>/plan_manager.js create <feature_plan_folder_full_path>/plan.json \'<json>\'',
      '3. Loop: call next → check resume flag → execute step → update_status complete → repeat',
      '4. resume:true = continue interrupted work; resume:false = start fresh',
      '5. Done when next returns count:0 and plan_status:complete',
    ],
  });
}

// ---------------------------------------------------------------------------
// Dispatch
// ---------------------------------------------------------------------------

const [,, cmd, planFile, ...args] = process.argv;

if (!cmd) {
  cmdHelp();
  process.exit(0);
}

switch (cmd) {
  case 'help':          cmdHelp(); break;
  case 'create':        cmdCreate(planFile, JSON.parse(args[0] || '{}')); break;
  case 'next':          cmdNext(planFile, parseInt(args[0] || '10', 10)); break;
  case 'update_status': cmdUpdateStatus(planFile, args[0], args[1]); break;
  case 'show_status':   cmdShowStatus(planFile, args[0]); break;
  case 'query':         cmdQuery(planFile, args[0]); break;
  case 'upsert':        cmdUpsert(planFile, args[0], JSON.parse(args[1] || '{}')); break;
  default:
    out({ error: `unknown_command: ${cmd}`, commands: ['help', 'create', 'next', 'update_status', 'show_status', 'query', 'upsert'] });
    process.exit(1);
}
