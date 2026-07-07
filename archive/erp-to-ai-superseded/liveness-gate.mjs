#!/usr/bin/env node
/**
 * liveness-gate.mjs — the liveness GATE for the ERP-to-AI Engineering mode.
 *
 * The filter step (filter-ai-title-sponsors.py) ranks employers by their H-1B
 * title-filing history. That signal is historical: it says a company sponsored
 * applied-AI titles in the past, NOT that a role is open now. This wrapper closes
 * that gap by reusing the repo's tested liveness checker (scripts/ats/
 * liveness-browser.mjs, the same logic behind `npm run ats:liveness`) to test
 * whether a real posting URL is live.
 *
 * Liveness is a GATE, not a vote: only `active` clears it. `expired` or
 * `uncertain` closes the gate for that company -> the mode must not recommend
 * Apply, no matter how strong the sponsorship history.
 *
 * Usage:
 *   node scripts/ai-pivot/liveness-gate.mjs --file <urls.txt> [--out logs/...json]
 *
 * urls.txt format (one per line):  Company Name | https://job-posting-url
 * Lines starting with # are ignored.
 *
 * Exit code: 0 if every URL is active; 1 if any gate is closed (expected when a
 * posting has expired — a closed gate is a successful, informative outcome).
 */

import { chromium } from 'playwright';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { checkUrlLiveness } from '../ats/liveness-browser.mjs';

function parseArgs(argv) {
  const args = { file: null, out: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--file') args.file = argv[++i];
    else if (argv[i] === '--out') args.out = argv[++i];
  }
  return args;
}

function today() {
  return new Date().toISOString().slice(0, 10).replace(/-/g, '');
}

async function main() {
  const { file, out } = parseArgs(process.argv.slice(2));
  if (!file) {
    console.error('Usage: node scripts/ai-pivot/liveness-gate.mjs --file <urls.txt> [--out <json>]');
    process.exit(2);
  }

  const text = await readFile(file, 'utf-8');
  const entries = text
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith('#'))
    .map((l) => {
      const idx = l.indexOf('|');
      if (idx === -1) return { company: '(unlabeled)', url: l };
      return { company: l.slice(0, idx).trim(), url: l.slice(idx + 1).trim() };
    });

  if (entries.length === 0) {
    console.error('STOP: no URLs to check — the gate refuses to pass an empty set.');
    process.exit(2);
  }

  console.log(`Liveness gate: checking ${entries.length} posting(s)...\n`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const results = [];
  let passed = 0;
  let closed = 0;

  // Sequential — repo rule: never Playwright in parallel.
  for (const { company, url } of entries) {
    const { result, reason } = await checkUrlLiveness(page, url);
    const gate = result === 'active' ? 'PASS' : 'CLOSED';
    const icon = { active: 'PASS ', expired: 'CLOSED', uncertain: 'CLOSED' }[result] || 'CLOSED';
    console.log(`[${icon}] ${result.padEnd(9)} ${company} — ${url}`);
    if (result !== 'active' && reason) console.log(`          reason: ${reason}`);
    results.push({ company, url, liveness: result, gate, reason: reason || null });
    if (gate === 'PASS') passed++;
    else closed++;
  }

  await browser.close();

  const log = {
    workflow: 'case-erp-to-ai-engineering',
    gate: 'liveness',
    generated_at: new Date().toISOString(),
    checker: 'scripts/ats/liveness-browser.mjs (same logic as npm run ats:liveness)',
    checked: entries.length,
    passed,
    closed,
    gate_rule: 'only result=active clears the gate; expired/uncertain closes it',
    results,
  };

  const outPath = out || path.join('logs', `case-erp-to-ai-engineering-liveness-${today()}.json`);
  await mkdir(path.dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(log, null, 2));

  console.log(`\nGate results: ${passed} PASS  ${closed} CLOSED`);
  console.log(`Gate log: ${outPath}`);
  if (closed > 0) process.exit(1);
}

main().catch((err) => {
  console.error('Fatal:', err.message);
  process.exit(1);
});
