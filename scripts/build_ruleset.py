#!/usr/bin/env python3

import json
import sys
import urllib.request
from pathlib import Path


def download(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def build(source: str):
    domains = set()
    suffixes = set()
    keywords = set()

    for line in source.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "," not in line:
            continue

        rule, value = line.split(",", 1)

        rule = rule.strip().upper()
        value = value.strip().lower().rstrip(".")

        if not value:
            continue

        if rule == "DOMAIN":
            domains.add(value)

        elif rule == "DOMAIN-SUFFIX":
            suffixes.add(value)

        elif rule == "DOMAIN-KEYWORD":
            keywords.add(value)

    rule = {}

    if domains:
        rule["domain"] = sorted(domains)

    if suffixes:
        rule["domain_suffix"] = sorted(suffixes)

    if keywords:
        rule["domain_keyword"] = sorted(keywords)

    return {
        "version": 3,
        "rules": [rule]
    }


def main():

    if len(sys.argv) != 3:
        print("Usage:")
        print("build_ruleset.py <URL> <OUTPUT_JSON>")
        sys.exit(1)

    url = sys.argv[1]
    output = Path(sys.argv[2])

    print(f"Downloading {url}")

    text = download(url)

    ruleset = build(text)

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(ruleset, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print(f"Saved {output}")


if __name__ == "__main__":
    main()
