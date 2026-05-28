#!/usr/bin/env python3
"""Check that all URLs cited in <References> blocks across content files return HTTP 2xx.

Usage:
    python scripts/link-check.py            # check all
    python scripts/link-check.py --json     # emit machine report

Writes scripts/link-check-report.json.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
URL_RE = re.compile(r"url:\s*[\"']([^\"']+)[\"']")
TIMEOUT = 15
USER_AGENT = "AncientPhilosophiaLinkCheck/1.0 (+https://ancient-philosophia.org)"


def collect_urls() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for path in CONTENT.rglob("*.md*"):
        urls = list(dict.fromkeys(URL_RE.findall(path.read_text(encoding="utf-8"))))
        if urls:
            out[str(path.relative_to(ROOT))] = urls
    return out


def check(url: str) -> tuple[str, int | str]:
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT,
                          headers={"User-Agent": USER_AGENT})
        if r.status_code >= 400 or r.status_code == 405:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT, stream=True,
                             headers={"User-Agent": USER_AGENT})
        return url, r.status_code
    except requests.RequestException as e:
        return url, type(e).__name__


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    by_file = collect_urls()
    all_urls = sorted({u for urls in by_file.values() for u in urls})
    print(f"Checking {len(all_urls)} unique URLs across {len(by_file)} files…", file=sys.stderr)

    results: dict[str, int | str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for url, status in pool.map(check, all_urls):
            results[url] = status

    broken: list[dict] = []
    for path, urls in by_file.items():
        for u in urls:
            s = results[u]
            ok = isinstance(s, int) and s < 400
            if not ok:
                broken.append({"file": path, "url": u, "status": s})

    summary = {
        "checked": len(all_urls),
        "files": len(by_file),
        "broken": len(broken),
        "details": broken,
    }
    report_path = ROOT / "scripts" / "link-check-report.json"
    report_path.write_text(json.dumps(summary, indent=2))

    if args.json:
        json.dump(summary, sys.stdout, indent=2)
    else:
        if broken:
            print(f"\n{len(broken)} broken links:", file=sys.stderr)
            for b in broken:
                print(f"  [{b['status']}] {b['url']}  ({b['file']})", file=sys.stderr)
            print(f"\nReport: {report_path}", file=sys.stderr)
        else:
            print("All links OK ✓", file=sys.stderr)

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
