# Mystilink 八字计算器

> Languages: [English](README.md) | [简体中文](README.zh-CN.md)

## 概述

计算八字四柱、大运与流年，输出结构化 JSON，便于应用与脚本集成。不包含图片或 CDN 资源。

## 平台与语言

| 目标 | 交付 |
|------|------|
| Python | 可安装包 `mystilink-bazi-calculator` 与 CLI `mystilink-bazi` |
| JavaScript / Node | `bindings/js` 下的 npm 包（调用 CLI；浏览器通过可注入的 `runCli`） |
| C | 头文件 + 库，调用 CLI 并返回 JSON 字符串 |
| C++ | 对 C API 的薄封装 |
| C# | 通过进程启动 CLI |
| Java | 通过 ProcessBuilder 启动 CLI |

除 Python 外，绑定均调用 `PATH` 上的 `mystilink-bazi`（或环境变量 `MYSTILINK_BAZI_CLI`）。

## 环境要求

- Python 3.9 及以上
- 使用语言绑定时：CLI 须已安装并可在 `PATH` 中找到

## 安装与快速开始

```bash
# 在本地获取仓库之后
cd mystilink-bazi-calculator
python3 -m pip install -e .
mystilink-bazi calculate --date 1990-05-15 --hour 12

# 可选 lunar 引擎（Python 3.10+）
python3 -m pip install -e '.[lunar]'
mystilink-bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

也可：

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## 命令行

成功时向标准输出打印 JSON。

```bash
mystilink-bazi calculate --date YYYY-MM-DD [--hour N] [--minute N] [--timezone IANA] [--longitude N]
mystilink-bazi calculate --birth-json path/or/-/inline.json
mystilink-bazi calculate --calendar-basis path/or/-/basis.json
mystilink-bazi calculate --date YYYY-MM-DD --hour N --timezone IANA --calendar-engine lunar
mystilink-bazi dayun --date YYYY-MM-DD --gender male|female [--count N]
mystilink-bazi liunian --year YYYY [--day-stem STEM] [--pillars-json JSON]
mystilink-bazi version
```

### calculate

| 参数 | 说明 |
|------|------|
| `--date` | 出生日期 `YYYY-MM-DD`（未使用 `--birth-json` / `--calendar-basis` 时必填） |
| `--hour` | 出生小时 `0-23`（省略时默认 `11`） |
| `--minute` | 出生分钟 `0-59`（默认 `0`） |
| `--timezone` | IANA 时区（真太阳时 / lunar 引擎 / 可选输出 `birth` 块） |
| `--longitude` | 经度（度，东经为正） |
| `--birth-json` | BirthProfile（`mystilink.birth/0.1`）：文件路径、`-`（标准输入）或内联 JSON |
| `--calendar-engine` | `builtin`（默认）、`lunar`（可选 extra）或 `external_basis` |
| `--calendar-basis` | 外部 calendar-basis / lunar convert JSON；不 import lunar |

真太阳时：旧 CLI 在同时提供 `--timezone` 与 `--longitude` 时启用；BirthProfile 仅在 `birth.true_solar_time` 为 true 且时区/经度齐全时启用。

每柱含 `stem_index`、`branch_index`、`text`，并保留旧字段 `stem` / `branch` / `ganzhi`（`ganzhi` 与 `text` 相同）。顶层 `schema_version` 为 `mystilink.bazi.chart/0.1`；`bazi_schema_version` 仍为 `1.0` 以兼容旧消费者。`calendar_engine` 为 `builtin` / `lunar` / `external_basis`。

### dayun

| 参数 | 说明 |
|------|------|
| `--date` | 出生日期（必填） |
| `--gender` | `male` 或 `female`（必填） |
| `--count` | 大运步数（默认 `8`） |

### liunian

| 参数 | 说明 |
|------|------|
| `--year` | 目标公历年份（必填） |
| `--day-stem` | 日主天干，用于十神标注 |
| `--pillars-json` | 原局四柱 JSON，用于作用关系提示 |

## Python API

```python
from datetime import date
from mystilink_bazi import (
    compute_bazi,
    compute_bazi_from_calendar_basis,
    compute_bazi_with_lunar,
    compute_dayun,
    compute_liunian,
)

pillars = compute_bazi(date(1990, 5, 15), hour_interval=12, minute=0)
# 可选: compute_bazi_with_lunar(..., timezone="Asia/Shanghai")
# 可选: compute_bazi_from_calendar_basis(basis_dict)
dayun = compute_dayun(date(1990, 5, 15), "male", count=8)
liunian = compute_liunian(2024, day_stem=pillars["pillars"]["day"]["stem"])
```

## 兼容性

- 可单独安装：不硬依赖 `mystilink-lunar` 或 metaphysics-schema 包。
- 可选 lunar：`pip install 'mystilink-bazi-calculator[lunar]'`（需 Python 3.10+）。
- 无 import 编排：`mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`。
- 契约对齐：输出字段对齐 `mystilink.bazi.chart/0.1` / Ganzhi；BirthProfile 输入按 `mystilink.birth/0.1` 字段约定解析。
- 变更见 [CHANGELOG.md](CHANGELOG.md)。

## 示例

可运行示例位于 `examples/{c,cpp,csharp,java,js,node,python}/`。各语言绑定源码位于 `bindings/`。

CLI JSON 结构说明见 `schema/`。样例：

- BirthProfile：`tests/fixtures/birth.profile.v0.json`
- Calendar basis：`tests/fixtures/calendar.basis.v0.json`

```bash
mystilink-bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
mystilink-bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```

## 限制

- 大运起运所用节气日期为公历近似日，非天文精密历。
- 真太阳时基于均时差与经度；精度取决于时区与经度输入。
- 本包不附带字体、图片或远程资源查询。
- 内置历法规则为近似实现，不能替代专用农历/星历库。

## 许可

MIT。见 [LICENSE](LICENSE)。

## 问题反馈

反馈时请附带：CLI 版本（`mystilink-bazi version`）、完整命令行（仅用虚构日期）、以及 stderr/stdout 中的 JSON。
