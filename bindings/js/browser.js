'use strict';

/**
 * Browser entry: same API as Node, but requires an injected `runCli`.
 *
 * Example:
 *   const api = createBaziApi(async (args) => {
 *     // bridge to a local Node/host that runs mystilink-bazi
 *     return JSON.parse(await host.run('mystilink-bazi', args));
 *   });
 */

function createBaziApi(runCli) {
  if (typeof runCli !== 'function') {
    throw new Error('createBaziApi requires a runCli(args) function that returns parsed JSON');
  }

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

  function dayun(options) {
    const args = ['dayun', '--date', String(options.date), '--gender', String(options.gender)];
    if (options.count !== undefined && options.count !== null) {
      args.push('--count', String(options.count));
    }
    return runCli(args);
  }

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

  return { calculate, dayun, liunian, version, runCli };
}

module.exports = { createBaziApi };

if (typeof window !== 'undefined') {
  window.MystiLinkBazi = { createBaziApi };
}
