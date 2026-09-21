# Mystilink 八字計算器

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 概述

計算八字四柱、大運與流年，輸出結構化 JSON，便於應用與腳本整合。不包含圖片或 CDN 資源。

## 平台與語言

| 目標 | 交付 |
|------|------|
| Python | 可安裝套件 `mystilink-bazi-calculator` 與 CLI `bazi` |
| JavaScript / Node | `bindings/js` 下的 npm 套件（呼叫 CLI；瀏覽器透過可注入的 `runCli`） |
| C | 標頭檔 + 函式庫，呼叫 CLI 並回傳 JSON 字串 |
| C++ | 對 C API 的薄封裝 |
| C# | 透過行程啟動 CLI |
| Java | 透過 ProcessBuilder 啟動 CLI |

除 Python 外，綁定均呼叫 `PATH` 上的 `bazi`（或環境變數 `MYSTILINK_BAZI_CLI`）。長別名 `mystilink-bazi` 仍會安裝以保持相容。

## 環境需求

- Python 3.9 及以上
- 使用語言綁定時：CLI 須已安裝並可在 `PATH` 中找到

## 安裝與快速開始

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
bazi calculate --date 1990-05-15 --hour 12

# optional lunar engine (Python 3.10+)
python3 -m pip install -e '.[lunar]'
bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

亦可以：

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

成功時向標準輸出列印 JSON。

```bash
bazi calculate --date YYYY-MM-DD [--hour N] [--minute N] [--timezone IANA] [--longitude N]
bazi calculate --birth-json path/or/-/inline.json
bazi calculate --calendar-basis path/or/-/basis.json
bazi calculate --date YYYY-MM-DD --hour N --timezone IANA --calendar-engine lunar
bazi dayun --date YYYY-MM-DD --gender male|female [--count N]
bazi liunian --year YYYY [--day-stem STEM] [--pillars-json JSON]
bazi version
```

### calculate

| 選項 | 說明 |
|------|------|
| `--date` | 出生日期 `YYYY-MM-DD`（未使用 `--birth-json` 或 `--calendar-basis` 時必填） |
| `--hour` | 出生小時 `0-23`（省略時預設 `11`） |
| `--minute` | 出生分鐘 `0-59`（預設 `0`） |
| `--timezone` | IANA 時區（真太陽時 / lunar 引擎 / 可選輸出 `birth` 區塊） |
| `--longitude` | 經度（度，東經為正） |
| `--birth-json` | BirthProfile（`mystilink.birth/0.1`）：檔案路徑、`-`（標準輸入）或內嵌 JSON |
| `--calendar-engine` | `builtin`（預設）、`lunar`（可選 extra）或 `external_basis` |
| `--calendar-basis` | 外部 calendar-basis / lunar convert JSON；不 import lunar |

真太陽時僅在同時設定 `--timezone` 與 `--longitude` 時套用（舊版 CLI），或當 BirthProfile 設定 `birth.true_solar_time` **且**時區/經度可用時。

每柱含 `stem_index`、`branch_index`、`text`，並保留舊欄位 `stem` / `branch` / `ganzhi`（`ganzhi` 等於 `text`）。頂層 `schema_version` 為 `mystilink.bazi.chart/0.1`；`bazi_schema_version` 仍為 `1.0` 以相容舊消費者。`calendar_engine` 回報 `builtin`、`lunar` 或 `external_basis`。

### dayun

| 選項 | 說明 |
|------|------|
| `--date` | 出生日期（必填） |
| `--gender` | `male` 或 `female`（必填） |
| `--count` | 大運步數（預設 `8`） |

### liunian

| 選項 | 說明 |
|------|------|
| `--year` | 目標公曆年份（必填） |
| `--day-stem` | 日主天干，用於十神標註 |
| `--pillars-json` | 原局四柱 JSON，用於作用關係提示 |

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
# optional: compute_bazi_with_lunar(..., timezone="Asia/Shanghai")
# optional: compute_bazi_from_calendar_basis(basis_dict)
dayun = compute_dayun(date(1990, 5, 15), "male", count=8)
liunian = compute_liunian(2024, day_stem=pillars["pillars"]["day"]["stem"])
```

## 相容性

- 可單獨安裝：不硬依賴 `mystilink-lunar` 或 metaphysics-schema 套件。
- 可選 lunar：`pip install 'mystilink-bazi-calculator[lunar]'`（需 Python 3.10+）。
- 無 import 編排：`mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`。
- 契約對齊：輸出欄位對齊 `mystilink.bazi.chart/0.1` / Ganzhi 形狀；BirthProfile 輸入依 `mystilink.birth/0.1` 欄位慣例解析。
- 見 [CHANGELOG.md](../../CHANGELOG.md)。

## 範例

可執行範例位於 `examples/{c,cpp,csharp,java,js,node,python}/`。各語言綁定原始碼位於 `bindings/`。

CLI JSON 結構說明見 `schema/`。樣例：

- BirthProfile：`tests/fixtures/birth.profile.v0.json`
- Calendar basis：`tests/fixtures/calendar.basis.v0.json`

```bash
bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```


可選 `--envelope` 將結果包裝為 `mystilink.envelope/0.1`（預設仍為裸 JSON）。

## 限制

- 大運起運所用節氣日期為公曆近似日，非天文精密曆。
- 真太陽時基於均時差與經度；精度取決於時區與經度輸入。
- 本套件不附帶字型、圖片或遠端資源查詢。
- 內建曆法規則為近似實作，不能取代專用農曆/星曆庫。

## 授權

MIT。見 [LICENSE](../../LICENSE)。

## 問題回報

回報時請附帶：CLI 版本（`mystilink-bazi version`）、完整命令列（僅用虛構日期）、以及 stderr/stdout 中的 JSON。
