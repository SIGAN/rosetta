'use strict';
// adapter.js — IDE input normalization adapter for Rosetta hooks
// Normalizes stdin from any supported IDE to/from the Claude Code canonical format.
// Exports: detectIDE, normalize, formatOutput, readStdin

// Claude Code sends all three of these fields on every hook event
const CC_SIGNATURE = ['hook_event_name', 'tool_input', 'session_id'];

/**
 * Detect which IDE sent the input based on field shape heuristics.
 * @param {object} rawInput
 * @returns {'claude-code'}
 * @throws {Error} for null/non-object input or unrecognized IDE shape
 */
function detectIDE(rawInput) {
  if (rawInput === null || rawInput === undefined) {
    throw new Error('Invalid input: null or undefined');
  }
  if (typeof rawInput !== 'object' || Array.isArray(rawInput)) {
    throw new Error('Invalid input: expected a plain object');
  }
  if (CC_SIGNATURE.every((field) => field in rawInput)) {
    return 'claude-code';
  }
  throw new Error(`Unsupported IDE: ${JSON.stringify(Object.keys(rawInput))}`);
}

/**
 * Normalize any IDE input to Claude Code canonical format.
 * Claude Code input is already canonical — identity pass-through.
 * @param {object} rawInput
 * @returns {object} canonical input
 * @throws {Error} for unsupported IDE shapes
 */
function normalize(rawInput) {
  const ide = detectIDE(rawInput); // throws for unsupported
  if (ide === 'claude-code') {
    return rawInput;
  }
  // Future IDEs: add field-mapping branches here when real fixtures are captured
  throw new Error(`Unsupported IDE: ${ide}`);
}

/**
 * Convert canonical output to IDE-specific output format.
 * Claude Code output is already canonical — identity pass-through.
 * @param {object} canonicalOutput
 * @param {string} ide
 * @returns {object}
 */
function formatOutput(canonicalOutput, ide) {
  // claude-code: identity pass-through
  // other IDEs: identity until real output schemas are captured from real stdin dumps
  return canonicalOutput;
}

/**
 * Read and parse JSON from stdin (or injected stream for testing).
 * @param {import('stream').Readable} [stream]
 * @returns {Promise<object>}
 * @throws {Error} on empty or invalid JSON
 */
async function readStdin(stream = process.stdin) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    stream.on('data', (chunk) => chunks.push(String(chunk)));
    stream.on('end', () => {
      const raw = chunks.join('').trim();
      if (!raw) {
        return reject(new Error('Invalid input: empty stdin'));
      }
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(new Error(`JSON parse error: ${err.message}`));
      }
    });
    stream.on('error', reject);
  });
}

module.exports = { readStdin, normalize, formatOutput, detectIDE };
