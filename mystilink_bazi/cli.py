# -*- coding: utf-8 -*-
"""CLI for Mystilink BaZi calculator. Prints JSON to stdout on success."""
from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mystilink_bazi.birth import BirthProfileError, parse_birth_profile
from mystilink_bazi.calculate import compute_bazi, parse_date, resolve_birth_datetime
from mystilink_bazi.calendar_engine import (
    CalendarEngineError,
    compute_bazi_from_calendar_basis,
    compute_bazi_with_lunar,
)
from mystilink_bazi.dayun import compute_dayun
from mystilink_bazi.liunian import compute_liunian

PACKAGE_NAME = "mystilink-bazi-calculator"
FALLBACK_VERSION = "0.2.2"


def get_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return FALLBACK_VERSION


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _print_error(message: str, code: int = 1) -> None:
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(code)


def _load_json_arg(raw: str) -> Dict[str, Any]:
    """Load JSON from a file path, '-' (stdin), or an inline JSON string."""
    text: str
    if raw == "-":
        text = sys.stdin.read()
    else:
        path = Path(raw)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
        else:
            text = raw
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def _resolve_calculate_inputs(
    args: argparse.Namespace,
) -> Tuple[Any, int, int, Optional[str], Optional[float], bool]:
    """
    Return (birth_date, hour, minute, timezone, longitude, prefer_true_solar).

    BirthProfile (--birth-json) takes precedence for civil time; CLI flags may
    still override timezone/longitude when explicitly set.
    """
    prefer_true_solar = False
    timezone: Optional[str] = args.timezone
    longitude: Optional[float] = args.longitude

    if args.birth_json:
        try:
            profile = _load_json_arg(args.birth_json)
            civil, hour, minute, tz, lon = parse_birth_profile(profile)
        except (BirthProfileError, ValueError, OSError) as exc:
            _print_error(str(exc))
        if timezone is None:
            timezone = tz
        if longitude is None:
            longitude = lon
        birth_block = profile.get("birth") if isinstance(profile.get("birth"), dict) else {}
        prefer_true_solar = bool(birth_block.get("true_solar_time"))
        return civil, hour, minute, timezone, longitude, prefer_true_solar

    if not args.date and not args.calendar_basis:
        _print_error("either --date, --birth-json, or --calendar-basis is required")

    if not args.date:
        # calendar-basis may supply solar civil time later
        return None, 11, 0, timezone, longitude, prefer_true_solar

    try:
        civil = parse_date(args.date)
    except Exception as exc:
        _print_error(str(exc))

    if args.hour is not None:
        hour = max(0, min(23, args.hour))
    elif args.hour_interval is not None:
        hour = max(0, min(23, args.hour_interval))
    else:
        hour = 11
    minute = max(0, min(59, args.minute))
    return civil, hour, minute, timezone, longitude, prefer_true_solar


def cmd_calculate(args: argparse.Namespace) -> None:
    birth, hi, mi, timezone, longitude, prefer_true_solar = _resolve_calculate_inputs(args)

    tst_enabled = False
    tst_delta = 0.0
    if birth is not None:
        if args.birth_json:
            apply_tst = prefer_true_solar and timezone is not None and longitude is not None
        else:
            apply_tst = timezone is not None and longitude is not None
        if apply_tst:
            try:
                birth, hi, mi, tst_enabled, tst_delta = resolve_birth_datetime(
                    birth, hi, mi, timezone, longitude  # type: ignore[arg-type]
                )
            except Exception as exc:
                print(
                    json.dumps(
                        {"warning": f"True solar time failed, using clock time: {exc}"},
                        ensure_ascii=False,
                    ),
                    file=sys.stderr,
                )
        elif prefer_true_solar and (timezone is None or longitude is None):
            print(
                json.dumps(
                    {
                        "warning": (
                            "true_solar_time requested but timezone/longitude missing; "
                            "using clock time"
                        )
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )

    engine = args.calendar_engine or "builtin"

    try:
        if args.calendar_basis:
            basis = _load_json_arg(args.calendar_basis)
            hour_arg = args.hour if args.hour is not None else args.hour_interval
            if birth is not None:
                out = compute_bazi_from_calendar_basis(
                    basis,
                    birth_date=birth,
                    hour=hi,
                    minute=mi,
                    timezone=timezone,
                    true_solar_enabled=tst_enabled,
                    true_solar_delta_minutes=tst_delta,
                )
            else:
                out = compute_bazi_from_calendar_basis(
                    basis,
                    birth_date=None,
                    hour=hour_arg,
                    minute=args.minute if hour_arg is not None or args.minute else None,
                    timezone=timezone,
                    true_solar_enabled=tst_enabled,
                    true_solar_delta_minutes=tst_delta,
                )
        elif engine == "lunar":
            if birth is None:
                _print_error("--date or --birth-json is required for calendar_engine=lunar")
            if not timezone:
                _print_error("calendar_engine=lunar requires --timezone (IANA)")
            out = compute_bazi_with_lunar(
                birth,
                hi,
                mi,
                timezone=timezone,
                true_solar_enabled=tst_enabled,
                true_solar_delta_minutes=tst_delta,
            )
        elif engine == "builtin":
            if birth is None:
                _print_error("--date or --birth-json is required for calendar_engine=builtin")
            out = compute_bazi(
                birth,
                hi,
                mi,
                true_solar_enabled=tst_enabled,
                true_solar_delta_minutes=tst_delta,
                timezone=timezone,
                calendar_engine="builtin",
            )
        elif engine == "external_basis":
            _print_error(
                "calendar_engine=external_basis requires --calendar-basis JSON"
            )
        else:
            _print_error(f"unknown calendar_engine: {engine!r}")
    except CalendarEngineError as exc:
        _print_error(str(exc))
    except Exception as exc:
        _print_error(str(exc))

    _print_json(out)


def cmd_dayun(args: argparse.Namespace) -> None:
    try:
        birth = parse_date(args.date)
    except Exception as exc:
        _print_error(str(exc))
    out = compute_dayun(birth, args.gender, args.count)
    _print_json(out)


def cmd_liunian(args: argparse.Namespace) -> None:
    pillars = None
    if args.pillars_json:
        try:
            pillars = json.loads(args.pillars_json)
        except json.JSONDecodeError as exc:
            _print_error(f"Invalid pillars JSON: {exc}")
    out = compute_liunian(args.year, args.day_stem, pillars)
    _print_json(out)


def cmd_version(_: argparse.Namespace) -> None:
    _print_json({"name": PACKAGE_NAME, "version": get_version(), "cli": "bazi"})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bazi",
        description="BaZi four pillars, dayun, and liunian calculator (JSON stdout).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_calc = sub.add_parser("calculate", help="Compute four pillars")
    p_calc.add_argument(
        "--date",
        required=False,
        default=None,
        help="Birth date YYYY-MM-DD (required unless --birth-json or --calendar-basis)",
    )
    p_calc.add_argument("--hour", type=int, default=None, help="Birth hour 0-23")
    p_calc.add_argument(
        "--hour-interval",
        type=int,
        default=None,
        help="Alias for --hour (0-23). Default 11 if both omitted.",
    )
    p_calc.add_argument("--minute", type=int, default=0, help="Birth minute 0-59")
    p_calc.add_argument(
        "--timezone",
        type=str,
        default=None,
        help="IANA timezone for true solar time / lunar engine (e.g. Asia/Shanghai)",
    )
    p_calc.add_argument(
        "--longitude",
        type=float,
        default=None,
        help="Longitude in degrees (east positive) for true solar time",
    )
    p_calc.add_argument(
        "--birth-json",
        type=str,
        default=None,
        help=(
            "BirthProfile JSON (mystilink.birth/0.1): file path, '-' for stdin, "
            "or inline JSON. Overrides --date/--hour/--minute when set."
        ),
    )
    p_calc.add_argument(
        "--calendar-engine",
        type=str,
        default="builtin",
        choices=["builtin", "lunar", "external_basis"],
        help=(
            "Pillar source: builtin (default), lunar (optional extra), "
            "or external_basis (use with --calendar-basis)"
        ),
    )
    p_calc.add_argument(
        "--calendar-basis",
        type=str,
        default=None,
        help=(
            "External calendar-basis / mystilink-lunar convert JSON "
            "(file, '-', or inline). Does not import lunar. Sets engine to external_basis."
        ),
    )
    p_calc.set_defaults(func=cmd_calculate)

    p_dayun = sub.add_parser("dayun", help="Compute decade fortune periods")
    p_dayun.add_argument("--date", required=True, help="Birth date YYYY-MM-DD")
    p_dayun.add_argument("--gender", required=True, choices=["male", "female"])
    p_dayun.add_argument("--count", type=int, default=8, help="Number of periods (default 8)")
    p_dayun.set_defaults(func=cmd_dayun)

    p_ln = sub.add_parser("liunian", help="Compute annual fortune")
    p_ln.add_argument("--year", type=int, required=True, help="Target solar year")
    p_ln.add_argument("--day-stem", type=str, default=None, help="Day stem for shishen")
    p_ln.add_argument(
        "--pillars-json",
        type=str,
        default=None,
        help='Four pillars JSON, e.g. {"year":{"stem":"甲","branch":"子"},...}',
    )
    p_ln.set_defaults(func=cmd_liunian)

    p_ver = sub.add_parser("version", help="Print package version as JSON")
    p_ver.set_defaults(func=cmd_version)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
