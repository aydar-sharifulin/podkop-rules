#!/usr/bin/env python3

import json
import urllib.request
from pathlib import Path

SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "misha-tgshv/shadowrocket-configuration-file/"
    "refs/heads/main/rules/domains_geo_detect.list"
)

OUTPUT_FILE = Path("rules/ip-checkers.json")


def main() -> None:
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as response:
        text = response.read().decode("utf-8")

    domains: set[str] = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("DOMAIN-SUFFIX,"):
            _, domain = line.split(",", 1)
            domain = domain.strip().lower().rstrip(".")

            if domain:
                domains.add(domain)

    if not domains:
        raise RuntimeError("No DOMAIN-SUFFIX entries found in source list")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 3,
        "rules": [
            {
                "domain_suffix": sorted(domains)
            }
        ]
    }

    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Created {OUTPUT_FILE} with {len(domains)} domains")


if __name__ == "__main__":
    main()
