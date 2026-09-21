# Mystilink 八字計算機

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 概要

中国八字（四柱）盤、大運、流年を計算します。結果はアプリケーションやスクリプト向けの構造化 JSON です。画像や CDN アセットは含まれません。

## プラットフォームと言語

| 対象 | 提供物 |
|------|--------|
| Python | インストール可能なパッケージ `mystilink-bazi-calculator` と CLI `bazi` |
| JavaScript / Node | `bindings/js` 配下の npm パッケージ（CLI を起動；ブラウザは注入可能な `runCli`） |
| C | CLI を呼び出して JSON を返すヘッダ + ライブラリ |
| C++ | C API 上の薄いラッパー |
| C# | CLI のプロセスラッパー |
| Java | CLI の ProcessBuilder ラッパー |

Python 以外のバインディングはすべて `PATH` 上の `bazi`（または `MYSTILINK_BAZI_CLI`）を呼び出します。互換のため長い別名 `mystilink-bazi` もインストールされます。

## 要件

- Python 3.9 以降
- 言語バインディング利用時：CLI がインストールされ `PATH` で利用可能であること

## インストールとクイックスタート

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
bazi calculate --date 1990-05-15 --hour 12

# optional lunar engine (Python 3.10+)
python3 -m pip install -e '.[lunar]'
bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

または：

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

成功時は常に stdout に JSON を出力します。

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

| オプション | 説明 |
|-----------|------|
| `--date` | 生年月日 `YYYY-MM-DD`（`--birth-json` または `--calendar-basis` 未使用時は必須） |
| `--hour` | 出生時 `0-23`（省略時デフォルト `11`） |
| `--minute` | 出生分 `0-59`（デフォルト `0`） |
| `--timezone` | IANA タイムゾーン（真太陽時 / lunar エンジン / 任意の `birth` ブロック） |
| `--longitude` | 経度（度、東経を正） |
| `--birth-json` | BirthProfile（`mystilink.birth/0.1`）：ファイルパス、`-`（stdin）、またはインライン JSON |
| `--calendar-engine` | `builtin`（デフォルト）、`lunar`（任意 extra）、または `external_basis` |
| `--calendar-basis` | 外部 calendar-basis / lunar convert JSON；lunar を import しない |

真太陽時は、`--timezone` と `--longitude` の両方が設定された場合（レガシー CLI）、または BirthProfile が `birth.true_solar_time` を設定し **かつ** タイムゾーン/経度が利用可能な場合にのみ適用されます。

各柱には `stem_index`、`branch_index`、`text` があり、レガシーの `stem` / `branch` / `ganzhi`（`ganzhi` は `text` と等しい）も含まれます。トップレベルの `schema_version` は `mystilink.bazi.chart/0.1`；`bazi_schema_version` は旧コンシューマ向けに `1.0` のままです。`calendar_engine` は `builtin`、`lunar`、または `external_basis` を報告します。

### dayun

| オプション | 説明 |
|-----------|------|
| `--date` | 生年月日（必須） |
| `--gender` | `male` または `female`（必須） |
| `--count` | 大運の期間数（デフォルト `8`） |

### liunian

| オプション | 説明 |
|-----------|------|
| `--year` | 対象の太陽年（必須） |
| `--day-stem` | 十神ラベル用の日干 |
| `--pillars-json` | 相互作用ヒント用の原局四柱 JSON |

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

## 互換性

- 単独インストール可：`mystilink-lunar` や metaphysics-schema パッケージへのハード依存なし。
- 任意の lunar：`pip install 'mystilink-bazi-calculator[lunar]'`（Python 3.10+ が必要）。
- import なしの連携：`mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`。
- 契約整合：出力フィールドは `mystilink.bazi.chart/0.1` / Ganzhi 形状に一致；BirthProfile 入力は `mystilink.birth/0.1` のフィールド慣例のみ。
- [CHANGELOG.md](../../CHANGELOG.md) を参照。

## 例

実行可能なサンプルは `examples/{c,cpp,csharp,java,js,node,python}/` にあります。バインディングソースは `bindings/` にあります。

CLI JSON 形状のスキーマは `schema/` にあります。サンプル：

- BirthProfile：`tests/fixtures/birth.profile.v0.json`
- Calendar basis：`tests/fixtures/calendar.basis.v0.json`

```bash
bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```


任意の `--envelope` は結果を `mystilink.envelope/0.1` で包みます（デフォルトは裸の JSON）。

## 制限

- 大運起運用の節気日は近似の民用暦日であり、精密星暦ではありません。
- 真太陽時は均時差と経度を使用；精度はタイムゾーンと経度入力に依存します。
- 本パッケージはフォント、画像、リモートアセット検索を同梱しません。
- 組み込み暦法ルールは近似であり、専用の旧暦/星暦ライブラリの代替ではありません。

## ライセンス

MIT。[LICENSE](../../LICENSE) を参照。

## フィードバック

不具合報告時は次を添付：CLI バージョン（`mystilink-bazi version`）、正確なコマンドライン（架空の日付のみ）、stderr/stdout の JSON。
