# Podkop Rule Sets

Custom rule sets and helper scripts for **Podkop** and **sing-box**.

The project automatically builds and publishes binary **`.srs`** rule sets through GitHub Actions to provide predictable **domain-based routing** for OpenWrt routers.

Instead of relying primarily on large GeoIP databases, the recommended configuration uses compact domain rule sets that are easier to understand, maintain and troubleshoot while remaining compatible with Russian services, banking applications and Apple devices.

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
| `ip-checkers.srs` | IP detection services |
| `oisd_small.srs` | Recommended block list |
| `oisd_big.srs` | Aggressive block list |

---

## Optional Podkop Route Priority Patch

Some Podkop versions evaluate general **DIRECT** rules before user-defined **PROXY** domains.

The optional patch changes the evaluation order so that explicit proxy domains always take precedence over general DIRECT rule sets.

```text
BLOCK
        ↓
Explicit PROXY domains
        ↓
DIRECT domains
        ↓
Default PROXY
```

The patch only changes the **routing priority**.

It does **not** modify:

- sing-box
- DNS
- FakeIP
- proxy protocols
- rule sets

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
└── patch-podkop-route-priority.sh
```

Generated automatically during GitHub Actions:

```text
build/
output/
```

---

## Updating Podkop

```sh
podkop list_update
podkop restart
```

---

## Philosophy

This project intentionally prefers **small, transparent domain rule sets** over large GeoIP databases.

Benefits:

- predictable routing;
- easier troubleshooting;
- lower router CPU usage;
- faster updates;
- easier maintenance.

---

## License

MIT
