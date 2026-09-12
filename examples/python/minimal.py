#!/usr/bin/env python3
"""Minimal Python example using the installed package."""
from datetime import date

from mystilink_bazi import compute_bazi, compute_dayun, compute_liunian

birth = date(1990, 5, 15)
result = compute_bazi(birth, hour_interval=12, minute=0)
print("ganzhi:", result["bazi_ganzhi"])

dayun = compute_dayun(birth, "male", count=3)
print("dayun count:", len(dayun["dayun_list"]))

liunian = compute_liunian(2024, day_stem=result["pillars"]["day"]["stem"])
print("liunian:", liunian["ganzhi"], liunian.get("shishen"))
