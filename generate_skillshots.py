#!/usr/bin/env python3
"""
Generate a per-champion list of skillshot basic abilities in numeric form:
1=Q, 2=W, 3=E, 4=R

Data source:
- Meraki Analytics LoL static data (champion JSONs include an ability 'targeting' field)
  Repo describes the CDN + goals: https://github.com/meraki-analytics/lolstaticdata

Outputs:
- lol_skillshots.json
- lol_skillshots.csv
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import requests


BASE_DIR = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions/"
OUT_JSON = "lol_skillshots.json"
OUT_CSV = "lol_skillshots.csv"

# Your requested mapping:
KEY_TO_NUM = {"Q": 1, "W": 2, "E": 3, "R": 4}

# Heuristic: treat these targeting types as "skillshots"
SKILLSHOT_TARGETING = {"Direction", "Location", "Vector"}


def fetch_index_json_filenames() -> List[str]:
    html = requests.get(BASE_DIR, timeout=60).text
    # Index page lists files like Ahri.json, Ahri.msgpack, etc.
    names = sorted(set(re.findall(r'href="([^"]+\.json)"', html)))
    return [n for n in names if n.lower().endswith(".json")]


def is_skillshot_ability(ability_obj: Dict[str, Any]) -> bool:
    targeting = ability_obj.get("targeting")
    return targeting in SKILLSHOT_TARGETING


def champion_skillshot_numbers(champ: Dict[str, Any]) -> Tuple[List[int], List[str]]:
    """
    Returns:
      - numbers: sorted list like [1,3]
      - keys: sorted list like ["Q","E"]
    """
    abilities = champ.get("abilities", {})
    hit_keys: List[str] = []

    for key in ("Q", "W", "E", "R"):
        if key not in abilities:
            continue

        # Meraki format: abilities["Q"] is a list (handles form swaps / multi-parts)
        ability_variants = abilities.get(key) or []
        if any(is_skillshot_ability(v) for v in ability_variants if isinstance(v, dict)):
            hit_keys.append(key)

    nums = sorted(KEY_TO_NUM[k] for k in hit_keys)
    hit_keys.sort(key=lambda k: KEY_TO_NUM[k])
    return nums, hit_keys


def main() -> None:
    filenames = fetch_index_json_filenames()
    print(f"Found {len(filenames)} champion JSON files.")

    result: Dict[str, List[int]] = {}
    rows: List[Tuple[str, str, str]] = []

    session = requests.Session()
    for fn in filenames:
        url = BASE_DIR + fn
        champ = session.get(url, timeout=60).json()

        name = champ.get("name") or fn.replace(".json", "")
        nums, keys = champion_skillshot_numbers(champ)

        result[name] = nums
        rows.append((name, ",".join(map(str, nums)), ",".join(keys)))

    # Stable sorting by champion name
    result = dict(sorted(result.items(), key=lambda kv: kv[0].lower()))
    rows.sort(key=lambda r: r[0].lower())

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Champion", "SkillshotNumbers(1=Q,2=W,3=E,4=R)", "SkillshotKeys"])
        w.writerows(rows)

    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_CSV}")

    # Print a small preview
    print("\nPreview (first 25):")
    for i, (name, nums, keys) in enumerate(rows[:25], start=1):
        print(f"{name}: {nums}   ({keys})")


if __name__ == "__main__":
    main()
