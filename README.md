# Podkop Rule Sets

Custom rule sets and helper scripts for **Podkop** and **sing-box**.

The project automatically builds and publishes binary **`.srs`** rule sets through GitHub Actions.

The recommended configuration uses **domain-based routing** instead of relying primarily on large GeoIP databases. This makes routing easier to understand, maintain and troubleshoot while remaining compatible with Russian services, banking applications and Apple devices.

---

## Features

- Automatic GitHub Releases
- Domain-based DIRECT routing
- OISD ad & malware blocking
- Explicit PROXY exceptions
- Optimized for OpenWrt
- Compatible with Podkop and sing-box
- Optional Podkop route-priority patch

---

## Routing Model

```text
Private networks
        ↓
Bypass TProxy

        ↓
OISD
        ↓
BLOCK

        ↓
Explicit PROXY domains
        ↓
PROXY

        ↓
Russian & trusted domains
        ↓
DIRECT

        ↓
Everything else
        ↓
PROXY
```

---

## Rule Sets

| Rule Set | Description |
|----------|-------------|
| `ru-direct.srs` | Russian and trusted domains |
| `ip-checkers.srs` | IP detection and geolocation services |
| `oisd_small.srs` | Recommended ad & malware block list |
| `oisd_big.srs` | More aggressive blocking |

Latest release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/latest
```

---

## Optional Podkop Route Priority Patch

Some Podkop versions evaluate general **DIRECT** rules before user-defined **PROXY** domains.

The optional patch changes the evaluation order:

```text
BLOCK
        ↓
Explicit PROXY domains
        ↓
DIRECT domains
        ↓
Default PROXY
```

This guarantees that manually configured proxy domains always take precedence over general DIRECT rule sets.

The patch **only changes route evaluation order**.

It does **not** modify:

- sing-box
- DNS
- FakeIP
- proxy protocols
- generated rule sets

> Reapply the patch after upgrading Podkop because `/usr/bin/podkop` may be replaced.

---

## Repository Structure

```text
.github/
└── workflows/
    └── build.yml

allowlist/
├── oisd.txt
└── proxy-from-direct.txt

rules/
└── ru-direct.json

scripts/
├── build_ruleset.py
└── patch-podkop-proxy-priority.sh
```

Generated during GitHub Actions:

```text
build/
output/
```

---

## Updating Podkop

Update rule sets:

```sh
podkop list_update
```

Restart:

```sh
podkop restart
```

Clear sing-box cache:

```sh
podkop stop
rm -f /tmp/sing-box/cache.db
podkop start
```

---

## Philosophy

This project intentionally prefers **small, transparent domain rule sets** over large GeoIP databases.

Benefits:

- predictable routing;
- easier troubleshooting;
- smaller rule sets;
- faster updates;
- easier maintenance.

GeoIP can still be added if a particular installation requires it, but it is **not part of the recommended configuration**.

---
