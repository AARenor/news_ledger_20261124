#!/usr/bin/env python3
"""Rank open free bounties by expected payout and show their entry blockers."""

import json
import urllib.request

API = "https://make.fun/api/competitions?status=open&limit=100"
REQUIREMENTS = "https://make.fun/api/competitions/{}/requirements"


def blockers(slug: str) -> str:
    with urllib.request.urlopen(REQUIREMENTS.format(slug), timeout=30) as response:
        data = json.load(response)
    prerequisite = data.get("prerequisites")
    label = prerequisite.get("label", "?") if isinstance(prerequisite, dict) else "none"
    return f"needs: {label[:34]} | handed over: {data.get('handed_over_places')}"


def main() -> None:
    with urllib.request.urlopen(API, timeout=30) as response:
        items = json.load(response)["items"]
    rows = []
    for item in items:
        if item.get("entryFeesUsd") not in (None, "0.00"):
            continue
        entrants = max(int(item.get("submissionCount") or 0), 1)
        pot = float(item.get("potUsd") or 0)
        rows.append((pot / entrants, item["slug"], pot, len(item.get("rewards") or {}), entrants))
    rows.sort(reverse=True)
    print(f"free open bounties: {len(rows)}")
    for value, slug, pot, paid, entrants in rows[:12]:
        print(f"${value:6.3f} expected | {slug[:46]:46} | pot ${pot:7.2f} | {paid:3} paid | {entrants:6} entries | {blockers(slug)}")


if __name__ == "__main__":
    main()
