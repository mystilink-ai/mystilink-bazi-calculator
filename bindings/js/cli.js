'use strict';

const { spawnSync } = require('child_process');

/**
 * Resolve CLI path: MYSTILINK_BAZI_CLI env, else `mystilink-bazi` on PATH.
 * @returns {string}
 */
function resolveCli() {
  return process.env.MYSTILINK_BAZI_CLI || 'mystilink-bazi';
}

/**
 * Run mystilink-bazi with args; return parsed JSON from stdout.
 * @param {string[]} args
 * @param {{ cli?: string }} [opts]
 * @returns {object}
 */
function runCli(args, opts = {}) {
  const cli = opts.cli || resolveCli();
  const result = spawnSync(cli, args, {
    encoding: 'utf8',
    maxBuffer: 10 * 1024 * 1024,
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    const errText = (result.stderr || result.stdout || '').trim();
    throw new Error(errText || `mystilink-bazi exited with code ${result.status}`);
  }
  return JSON.parse(result.stdout);
}

/**
 * @param {{ date: string, hour?: number, minute?: number, timezone?: string, longitude?: number }} options
 */
function calculate(options) {
  const args = ['calculate', '--date', String(options.date)];
  if (options.hour !== undefined && options.hour !== null) {
    args.push('--hour', String(options.hour));
  }
  if (options.minute !== undefined && options.minute !== null) {
    args.push('--minute', String(options.minute));
  }
  if (options.timezone) {
    args.push('--timezone', String(options.timezone));
  }
  if (options.longitude !== undefined && options.longitude !== null) {
    args.push('--longitude', String(options.longitude));
  }
  return runCli(args);
}

/**
 * @param {{ date: string, gender: 'male'|'female', count?: number }} options
 */
function dayun(options) {
  const args = ['dayun', '--date', String(options.date), '--gender', String(options.gender)];
  if (options.count !== undefined && options.count !== null) {
    args.push('--count', String(options.count));
  }
  return runCli(args);
}

/**
 * @param {{ year: number, dayStem?: string, pillarsJson?: string|object }} options
 */
function liunian(options) {
  const args = ['liunian', '--year', String(options.year)];
  if (options.dayStem) {
    args.push('--day-stem', String(options.dayStem));
  }
  if (options.pillarsJson !== undefined && options.pillarsJson !== null) {
    const raw =
      typeof options.pillarsJson === 'string'
        ? options.pillarsJson
        : JSON.stringify(options.pillarsJson);
    args.push('--pillars-json', raw);
  }
  return runCli(args);
}

function version() {
  return runCli(['version']);
}

module.exports = {
  resolveCli,
  runCli,
  calculate,
  dayun,
  liunian,
  version,
};
