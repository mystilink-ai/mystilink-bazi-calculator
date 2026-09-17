# Changelog

## 0.2.0

- Pillar objects include `stem_index`, `branch_index`, and `text` (legacy `ganzhi` kept as alias of `text`)
- Output adds `schema_version` (`mystilink.bazi.chart/0.1`), `calendar_engine` (`builtin`), and optional `birth` when timezone is known
- CLI `calculate` accepts optional `--birth-json` (mystilink.birth/0.1 BirthProfile: file, `-` stdin, or inline JSON)
- Legacy `--date` / `--hour` / `--minute` / `--timezone` / `--longitude` remain supported
- No hard dependency on `mystilink-lunar` or metaphysics-schema packages

## 0.1.0

- Initial four-pillar, dayun, and liunian JSON CLI
