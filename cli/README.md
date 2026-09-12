# CLI shim notes

After `python3 -m pip install -e .` from the repository root, the console script
`mystilink-bazi` is available. Equivalent module form:

```bash
python3 -m mystilink_bazi <subcommand> ...
```

Override the executable used by language bindings with `MYSTILINK_BAZI_CLI`.
