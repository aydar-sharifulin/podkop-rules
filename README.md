# Rule Sets

Custom rule sets for **Podkop**, **sing-box**, and **Shadowrocket**.

This repository automatically downloads upstream rule lists, generates optimized rule sets, validates them, compiles binary **sing-box** rule sets, generates native **Shadowrocket** rule lists, and publishes everything through **GitHub Releases**.

The project follows a **domain-first routing model**, where routing decisions are primarily based on domain names rather than large GeoIP databases. This provides predictable routing, easier maintenance, and better compatibility with OpenWrt routers.

---

# Features

- Automatic GitHub Releases
- Domain-first routing
- Automatic DIRECT list merging
- OISD allowlist support
- Native sing-box `.srs`
- Native Shadowrocket `.list`
- IP checker bypass
- Optimized for OpenWrt
- Compatible with Podkop
- Fully automated CI/CD pipeline

---

# Routing Model

```text
Private networks
        ↓
Bypass TProxy

        ↓
OISD
        ↓
BLOCK

        ↓
DIRECT domains
        ↓
DIRECT

        ↓
Everything else
        ↓
PROXY
```

Routing is intentionally simple:

- trusted services → DIRECT
- advertisements & malware → BLOCK
- everything else → PROXY

---

# External Sources

The repository automatically builds rule sets from several upstream projects.

| Source | Purpose |
|---------|---------|
| domains_geo_detect.list | IP detection and geolocation services |
| Russia/outside-clashx.lst | Russian services that should bypass the proxy |
| OISD Big | Advertisement, tracking and malware blocking |
| OISD Small | Lightweight advertisement blocking |

Local repository data:

- `rules/ru-direct.json`
- `allowlist/oisd.txt`
- `allowlist/proxy-from-direct.txt`

---

# Rule Sets

## sing-box

Generated binary rule sets:

- `ru-direct.srs`
- `ip-checkers.srs`
- `oisd_small.srs`
- `oisd_big.srs`

---

## Shadowrocket

Generated native rule lists:

- `ru-direct.list`
- `proxy-from-direct.list`
- `ip-checkers.list`
- `oisd_small.list`
- `oisd_big.list`

The Shadowrocket rule lists are generated automatically from the same source data as the sing-box rule sets, ensuring identical routing behavior across both platforms.

---

# DIRECT Rule Generation

The published `ru-direct.srs` is generated automatically during every build.

The workflow merges:

- local `rules/ru-direct.json`
- upstream `Russia/outside-clashx.lst`

into one unified DIRECT rule set.

This allows maintaining a small local rule set while automatically incorporating trusted Russian services from upstream.

---

# Proxy Exceptions

Some domains should always use the proxy even if they are trusted services.

These domains are maintained in:

```text
allowlist/proxy-from-direct.txt
```

The file is automatically converted into:

- `proxy-from-direct.list`

for Shadowrocket.

This keeps the DIRECT list and proxy exceptions independent and easy to maintain.

---

# OISD Allowlist

Before compiling the OISD rule sets, GitHub Actions removes domains listed in:

```text
allowlist/oisd.txt
```

from both:

- `oisd_small`
- `oisd_big`

Typical examples include:

```text
appmetrica.yandex.net
uaas.yandex.ru
```

This preserves compatibility with applications such as Finuslugi while keeping OISD protection enabled.

---

# Build Pipeline

GitHub Actions automatically performs the following steps:

1. Downloads external rule lists.
2. Merges Russian DIRECT domains.
3. Applies the OISD allowlist.
4. Builds proxy exception lists.
5. Validates generated JSON files.
6. Verifies rule counts.
7. Downloads the required sing-box version.
8. Compiles binary `.srs` rule sets.
9. Generates native Shadowrocket rule lists.
10. Verifies all generated artifacts.
11. Publishes the latest GitHub Release.

The workflow runs:

- manually (`workflow_dispatch`);
- after repository changes;
- once every day.

---

# Repository Structure

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
└── build_ruleset.py
```

Generated during GitHub Actions:

```text
build/
output/
```

These directories contain temporary build artifacts and should not be committed.

---

# Latest Release

https://github.com/aydar-sharifulin/podkop-rules/releases/latest

Generated artifacts:

## sing-box

```text
ru-direct.srs
ip-checkers.srs
oisd_small.srs
oisd_big.srs
```

## Shadowrocket

```text
ru-direct.list
proxy-from-direct.list
ip-checkers.list
oisd_small.list
oisd_big.list
```

---

# Updating Podkop

Update rule sets:

```sh
podkop list_update
```

Restart Podkop:

```sh
podkop restart
```

Clear sing-box cache:

```sh
podkop stop
rm -f /tmp/sing-box/cache.db
podkop start
```

A reboot also clears the temporary cache:

```sh
reboot
```

---

# Philosophy

This project intentionally favors **domain-first routing** over large GeoIP databases.

Advantages:

- predictable routing;
- deterministic behavior;
- easier troubleshooting;
- simpler rule sets;
- faster updates;
- centralized management;
- no router-side customization;
- better compatibility with OpenWrt.

The router contains almost no routing logic.

All routing intelligence is centralized in this repository.

Updating GitHub Releases automatically updates routing behavior on every router without changing the router configuration.

---

# License

This repository contains generated rule sets built from publicly available upstream lists.

Please respect the licenses of the original upstream projects.
