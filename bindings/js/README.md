# @mystilink/bazi-calculator

Node and browser binding for the `mystilink-bazi` CLI.

## Prerequisites

Install the Python package so `mystilink-bazi` is on `PATH`, or set `MYSTILINK_BAZI_CLI` to the executable path.

## Node

```js
const bazi = require('@mystilink/bazi-calculator');
const result = bazi.calculate({ date: '1990-05-15', hour: 12 });
```

Local path (from this repo):

```js
const bazi = require('../../bindings/js');
```

## Browser

Browsers cannot spawn processes. Inject a `runCli` that talks to a local host running the CLI:

```js
const { createBaziApi } = require('@mystilink/bazi-calculator/browser');
const api = createBaziApi(async (args) => hostRunCli(args));
```
