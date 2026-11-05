#!/usr/bin/env python3
"""Fetch citation metrics from a public Google Scholar profile into data/scholar.json.

Usage: python scripts/fetch_scholar.py
Uses only the standard library. On any failure (blocked, CAPTCHA, layout change)
it exits non-zero WITHOUT touching the existing JSON, so the old values stay.
"""
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "scholar.json"
USER = "jCp59vcAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en"


def fetch():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(html):
    # Stats table: 3 rows (Citations, h-index, i10-index) x 2 cols (All, Since YYYY)
    vals = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    if len(vals) < 6:
        raise ValueError("stats table not found (blocked or layout changed)")
    v = [int(x) for x in vals[:6]]
    return {"citations": v[0], "h_index": v[2], "i10_index": v[4]}


def main():
    try:
        data = parse(fetch())
    except Exception as e:
        sys.exit(f"fetch_scholar failed, keeping previous data: {e}")
    data.update({"updated": date.today().isoformat(),
                 "url": f"https://scholar.google.com/citations?user={USER}&hl=en"})
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if {k: old.get(k) for k in ("citations", "h_index", "i10_index")} == \
       {k: data[k] for k in ("citations", "h_index", "i10_index")}:
        print("unchanged")
        return
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("updated", data)


if __name__ == "__main__":
    main()
