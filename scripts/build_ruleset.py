#!/usr/bin/env python3

import json
import sys
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError


SUPPORTED_RULES = {
    "DOMAIN": "domain",
    "DOMAIN-SUFFIX": "domain_suffix",
    "DOMAIN-KEYWORD": "domain_keyword",
}


def download(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "podkop-rules-builder/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read().decode("utf-8-sig")
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"Failed to download {url}: {error}") from error


def build_ruleset(source: str) -> dict:
    values: dict[str, set[str]] = {
        "domain": set(),
        "domain_suffix": set(),
        "domain_keyword": set(),
    }

    for raw_line in source.splitlines():
        line = raw_line.strip()

        if not line or line.startswith(("#", ";", "//")):
            continue

        # Surge-правила могут выглядеть так:
        # DOMAIN-SUFFIX,example.com,REJECT
        parts = [part.strip() for part in line.split(",")]

        if len(parts) < 2:
            continue

        rule_type = parts[0].upper()
        target_field = SUPPORTED_RULES.get(rule_type)

        if target_field is None:
            continue

        value = parts[1].lower().rstrip(".")

        if value:
            values[target_field].add(value)

    rule: dict[str, list[str]] = {}

    for field, items in values.items():
        if items:
            rule[field] = sorted(items)

    if not rule:
        raise RuntimeError("No supported domain rules found in source")

    total = sum(len(items) for items in values.values())

    print(
        f"Parsed {total} rules: "
        f"domain={len(values['domain'])}, "
        f"suffix={len(values['domain_suffix'])}, "
        f"keyword={len(values['domain_keyword'])}"
    )

    return {
        "version": 3,
        "rules": [rule],
    }


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python3 scripts/build_ruleset.py "
            "<SOURCE_URL> <OUTPUT_JSON>",
            file=sys.stderr,
        )
        raise SystemExit(2)

    source_url = sys.argv[1]
    output_path = Path(sys.argv[2])

    print(f"Downloading: {source_url}")

    source = download(source_url)
    ruleset = build_ruleset(source)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(ruleset, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
