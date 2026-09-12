# -*- coding: utf-8 -*-
"""CLI for Mystilink BaZi calculator. Prints JSON to stdout on success."""
from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any, List, Optional

from mystilink_bazi.calculate import compute_bazi, parse_date, resolve_birth_datetime
from mystilink_bazi.dayun import compute_dayun
from mystilink_bazi.liunian import compute_liunian

PACKAGE_NAME = "mystilink-bazi-calculator"
FALLBACK_VERSION = "0.1.0"


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


def cmd_calculate(args: argparse.Namespace) -> None:
    try:
        birth = parse_date(args.date)
    except Exception as exc:
        _print_error(str(exc))

    if args.hour is not None:
        hi = max(0, min(23, args.hour))
    elif args.hour_interval is not None:
        hi = max(0, min(23, args.hour_interval))
    else:
        hi = 11
    mi = max(0, min(59, args.minute))

    tst_enabled = False
    tst_delta = 0.0
    if args.timezone is not None and args.longitude is not None:
        try:
            birth, hi, mi, tst_enabled, tst_delta = resolve_birth_datetime(
                birth, hi, mi, args.timezone, args.longitude
            )
        except Exception as exc:
            print(
                json.dumps(
                    {"warning": f"True solar time failed, using clock time: {exc}"},
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )

    out = compute_bazi(
        birth,
        hi,
        mi,
        true_solar_enabled=tst_enabled,
        true_solar_delta_minutes=tst_delta,
    )
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
    _print_json({"name": PACKAGE_NAME, "version": get_version(), "cli": "mystilink-bazi"})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mystilink-bazi",
        description="BaZi four pillars, dayun, and liunian calculator (JSON stdout).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_calc = sub.add_parser("calculate", help="Compute four pillars")
    p_calc.add_argument("--date", required=True, help="Birth date YYYY-MM-DD")
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
        help="IANA timezone for true solar time (e.g. Asia/Shanghai)",
    )
    p_calc.add_argument(
        "--longitude",
        type=float,
        default=None,
        help="Longitude in degrees (east positive) for true solar time",
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
