'use strict';

/**
 * Browser-oriented example: inject a runCli bridge.
 * In a real host, runCli would forward args to a local mystilink-bazi process.
 */
const { createBaziApi } = require('../../bindings/js/browser');

async function demo(runCli) {
  const api = createBaziApi(runCli);
  const result = await Promise.resolve(api.calculate({ date: '1990-05-15', hour: 12 }));
  console.log('ganzhi:', result.bazi_ganzhi);
}

// When executed under Node for smoke testing, fall back to the real CLI spawn:
if (require.main === module) {
  const nodeApi = require('../../bindings/js');
  demo((args) => nodeApi.runCli(args)).catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { demo };
