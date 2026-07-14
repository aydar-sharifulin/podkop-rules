# Podkop Rule Sets

Custom rule sets for **Podkop** and **sing-box**.

This repository automatically generates and publishes binary **`.srs`** rule sets using GitHub Actions.

The project follows a **domain-first routing model**, where routing decisions are primarily based on domain names rather than large GeoIP databases. This provides predictable routing, easier maintenance and better compatibility with OpenWrt routers.

---

# Features

- Automatic GitHub Releases
- Domain-based DIRECT routing
- Automatic DIRECT exclusions
- OISD ad & malware blocking
- IP checker bypass
- Optimized for OpenWrt
- Compatible with Podkop and sing-box
- Fully automated build pipeline

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
Russian & trusted domains
        ↓
DIRECT

        ↓
Everything else
        ↓
PROXY
```

Routing decisions are intentionally kept simple:

- trusted Russian services → DIRECT
- advertisement and malware → BLOCK
- everything else → PROXY

---

# Rule Sets

## ru-direct.srs

Russian and trusted domains that should bypass the proxy.

Examples include:

- `.ru`
- `.рф`
- `.su`
- banking services
- government services
- Apple services
- manually maintained trusted domains

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ru-direct.srs
```

---

## ip-checkers.srs

IP detection and geolocation services.

Generated automatically from:

```text
https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/rules/domains_geo_detect.list
```

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ip-checkers.srs
```

These services are routed directly so they display the real ISP address instead of the proxy address.

---

## oisd_small.srs

Recommended OISD block list.

Designed for:

- OpenWrt
- mobile devices
- banking applications
- Apple ecosystem
- maximum compatibility

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_small.srs
```

---

## oisd_big.srs

More aggressive advertisement, tracking and malware blocking.

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_big.srs
```

Use either:

- `oisd_small.srs`

or

- `oisd_big.srs`

but not both.

---

# Automatic DIRECT Exclusions

The generated `ru-direct.srs` is not simply a compiled copy of `ru-direct.json`.

During every build GitHub Actions automatically removes domains that should always use PROXY.

The exclusions are collected from two sources:

## Shadowrocket custom proxy list

```text
https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/rules/custom-proxy.list
```

and

## Local exclusions

```text
allowlist/proxy-from-direct.txt
```

The resulting logic is:

```text
ru-direct.json

AND

NOT (
    custom-proxy.list
    OR
    proxy-from-direct.txt
)
```

This allows maintaining one common DIRECT list while selectively excluding domains that should always use the proxy.

---

# OISD Allowlist

Both generated OISD rule sets are filtered before compilation.

Domains listed in

```text
allowlist/oisd.txt
```

are automatically removed from:

- `oisd_small.srs`
- `oisd_big.srs`

Current examples:

```text
appmetrica.yandex.net
uaas.yandex.ru
```

This preserves compatibility with applications such as Finuslugi while keeping the rest of the OISD protection intact.

---

# Build Pipeline

GitHub Actions automatically performs the following steps:

1. Downloads external rule lists.
2. Generates sing-box JSON rule sets.
3. Applies the OISD allowlist.
4. Downloads Shadowrocket `custom-proxy.list`.
5. Reads local `proxy-from-direct.txt`.
6. Removes proxy domains from `ru-direct.json`.
7. Validates every generated JSON file.
8. Verifies rule counts.
9. Downloads the required sing-box version.
10. Compiles every JSON file into binary `.srs`.
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

These directories are temporary build artifacts and should not be committed.

---

# Latest Release

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/latest
```

Direct downloads:

```text
ru-direct.srs
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ru-direct.srs

ip-checkers.srs
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ip-checkers.srs

oisd_small.srs
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_small.srs

oisd_big.srs
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_big.srs
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

This project intentionally favors **domain-based routing** over large GeoIP databases.

Advantages:

- predictable routing;
- deterministic behavior;
- easier troubleshooting;
- simpler rule sets;
- faster updates;
- centralized management through GitHub;
- no router-side customization;
- better compatibility with OpenWrt.

GeoIP can still be added when required, but it is **not part of the recommended configuration**.

The router simply downloads the latest generated rule sets from GitHub Releases and applies them automatically.

---

# License

This repository contains generated rule sets built from publicly available upstream lists.

Please respect the licenses of the original upstream projects.
