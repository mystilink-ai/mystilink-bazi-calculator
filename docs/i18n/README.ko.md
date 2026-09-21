# Mystilink 사주 계산기

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 개요

중국 사주(사주팔자) 명식, 대운, 유년을 계산합니다. 결과는 애플리케이션과 스크립트에 적합한 구조화 JSON 입니다. 이미지나 CDN 자산은 포함되지 않습니다.

## 플랫폼 및 언어

| 대상 | 제공물 |
|------|--------|
| Python | 설치 가능 패키지 `mystilink-bazi-calculator` 및 CLI `bazi` |
| JavaScript / Node | `bindings/js` 아래 npm 패키지(CLI 실행; 브라우저는 주입 가능한 `runCli`) |
| C | CLI 를 호출해 JSON 을 반환하는 헤더 + 라이브러리 |
| C++ | C API 위의 얇은 래퍼 |
| C# | CLI 프로세스 래퍼 |
| Java | CLI ProcessBuilder 래퍼 |

Python 외 바인딩은 모두 `PATH` 상의 `bazi`(또는 `MYSTILINK_BAZI_CLI`)를 호출합니다. 호환을 위해 긴 별칭 `mystilink-bazi` 도 설치됩니다.

## 요구 사항

- Python 3.9 이상
- 언어 바인딩 사용 시: CLI 가 설치되어 `PATH` 에서 사용 가능해야 함

## 설치 및 빠른 시작

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
bazi calculate --date 1990-05-15 --hour 12

# optional lunar engine (Python 3.10+)
python3 -m pip install -e '.[lunar]'
bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

또한:

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

성공 시 항상 stdout 에 JSON 을 출력합니다.

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

| 옵션 | 설명 |
|------|------|
| `--date` | 생년월일 `YYYY-MM-DD`(`--birth-json` 또는 `--calendar-basis` 미사용 시 필수) |
| `--hour` | 출생 시 `0-23`(생략 시 기본 `11`) |
| `--minute` | 출생 분 `0-59`(기본 `0`) |
| `--timezone` | IANA 타임존(진태양시 / lunar 엔진 / 선택적 `birth` 블록) |
| `--longitude` | 경도(도, 동경 양수) |
| `--birth-json` | BirthProfile(`mystilink.birth/0.1`): 파일 경로, `-`(stdin), 또는 인라인 JSON |
| `--calendar-engine` | `builtin`(기본), `lunar`(선택 extra), 또는 `external_basis` |
| `--calendar-basis` | 외부 calendar-basis / lunar convert JSON; lunar 를 import 하지 않음 |

진태양시는 `--timezone` 과 `--longitude` 가 모두 설정된 경우(레거시 CLI), 또는 BirthProfile 이 `birth.true_solar_time` 을 설정하고 **그리고** 타임존/경도를 사용할 수 있을 때만 적용됩니다.

각 기둥에는 `stem_index`, `branch_index`, `text` 가 있으며, 레거시 `stem` / `branch` / `ganzhi`(`ganzhi` 는 `text` 와 동일)도 포함됩니다. 최상위 `schema_version` 은 `mystilink.bazi.chart/0.1`; `bazi_schema_version` 은 구 소비자용으로 `1.0` 을 유지합니다. `calendar_engine` 은 `builtin`, `lunar`, 또는 `external_basis` 를 보고합니다.

### dayun

| 옵션 | 설명 |
|------|------|
| `--date` | 생년월일(필수) |
| `--gender` | `male` 또는 `female`(필수) |
| `--count` | 대운 기간 수(기본 `8`) |

### liunian

| 옵션 | 설명 |
|------|------|
| `--year` | 대상 태양력 연도(필수) |
| `--day-stem` | 십신 라벨용 일간 |
| `--pillars-json` | 상호작용 힌트용 원국 사주 JSON |

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

## 호환성

- 단독 설치 가능: `mystilink-lunar` 또는 metaphysics-schema 패키지에 대한 하드 의존 없음.
- 선택 lunar: `pip install 'mystilink-bazi-calculator[lunar]'`(Python 3.10+ 필요).
- import 없는 오케스트레이션: `mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`.
- 계약 정렬: 출력 필드는 `mystilink.bazi.chart/0.1` / Ganzhi 형태와 일치; BirthProfile 입력은 `mystilink.birth/0.1` 필드 관례만.
- [CHANGELOG.md](../../CHANGELOG.md) 참조.

## 예제

실행 가능 샘플은 `examples/{c,cpp,csharp,java,js,node,python}/` 에 있습니다. 바인딩 소스는 `bindings/` 에 있습니다.

CLI JSON 형태의 스키마는 `schema/` 에 있습니다. 샘플:

- BirthProfile: `tests/fixtures/birth.profile.v0.json`
- Calendar basis: `tests/fixtures/calendar.basis.v0.json`

```bash
bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```


선택적 `--envelope` 는 결과를 `mystilink.envelope/0.1` 로 감쌉니다(기본은 원시 JSON).

## 제한

- 대운 기운에 쓰는 절기 날짜는 근사 민간력 일이며, 정밀 천문력이 아닙니다.
- 진태양시는 균시차와 경도를 사용; 정확도는 타임존과 경도 입력에 의존합니다.
- 이 패키지는 글꼴, 이미지, 원격 자산 조회를 포함하지 않습니다.
- 내장 달력 규칙은 근사 구현이며, 전용 음력/천문력 라이브러리를 대체하지 않습니다.

## 라이선스

MIT. [LICENSE](../../LICENSE) 참조.

## 피드백

결함 보고 시 첨부: CLI 버전(`mystilink-bazi version`), 정확한 명령줄(가상 날짜만), stderr/stdout JSON.
