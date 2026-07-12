# Podkop Rule Sets

Custom rule sets and helper scripts for Podkop / sing-box.

The rule sets are generated automatically by GitHub Actions and published as GitHub Releases.

The repository implements the following routing model:

```text
BLOCK
↓
Explicit PROXY exceptions
↓
Russian and trusted services → DIRECT
↓
Everything else → PROXY
```

This is useful when Russian services, banking applications, government websites and selected trusted platforms must work directly, while the rest of the traffic should use a proxy.

---

## Routing Policy

| Priority | Rule | Action |
|---:|---|---|
| 1 | OISD blocking list | BLOCK |
| 2 | Explicit user proxy domains | PROXY |
| 3 | Russian and trusted domain lists | DIRECT |
| 4 | Russian GeoIP ranges | DIRECT |
| 5 | Everything else | PROXY |

Explicit user proxy domains must be evaluated before the general DIRECT and GeoIP rules.

This is important for domains such as `habr.com`:

```text
habr.com
→ resolves to a Russian IP
→ matches GeoIP RU
→ would normally use DIRECT
```

A higher-priority explicit PROXY rule overrides GeoIP:

```text
habr.com
→ explicit PROXY rule
→ main-out
```

---

# Generated Rule Sets

## Direct

### `ru-direct.srs`

Domains that should normally bypass the proxy.

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ru-direct.srs
```

Typical entries include:

- `.ru`
- `.рф`
- `.su`
- Russian services
- banking and government services
- Apple services requiring direct access
- manually added trusted domains

The source file is:

```text
rules/ru-direct.json
```

The final generated rule is calculated as:

```text
ru-direct.json
AND
NOT (
    custom-proxy.list
    OR
    allowlist/proxy-from-direct.txt
)
```

This means that domains explicitly marked for PROXY are excluded from the generated DIRECT rule set.

---

### `ip-checkers.srs`

IP detection and geolocation services.

Generated automatically from:

```text
https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/rules/domains_geo_detect.list
```

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ip-checkers.srs
```

These services are routed directly so that they display the real ISP address rather than the proxy server address.

---

# Proxy Exceptions

Two sources are combined to exclude selected domains from `ru-direct.srs`.

## External proxy list

The workflow downloads:

```text
https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/rules/custom-proxy.list
```

Supported entries:

```text
DOMAIN,example.com
DOMAIN-SUFFIX,example.com
```

## Local proxy exceptions

Personal exceptions are stored in:

```text
allowlist/proxy-from-direct.txt
```

A plain domain is treated as `DOMAIN-SUFFIX`:

```text
habr.com
```

Equivalent explicit syntax:

```text
DOMAIN-SUFFIX,habr.com
```

An exact-domain rule can also be used:

```text
DOMAIN,www.example.com
```

The external and local proxy lists are combined:

```text
proxy exceptions =
custom-proxy.list
OR
allowlist/proxy-from-direct.txt
```

These domains are removed from the generated `ru-direct.srs`.

Important: removing a domain from `ru-direct.srs` does not by itself override GeoIP RU. For that reason, explicit proxy domains must also have a higher-priority PROXY route in Podkop.

---

# Block Lists

Two OISD-based blocking rule sets are available.

## `oisd_big.srs`

More aggressive advertising, tracking, telemetry and malicious-domain blocking.

Generated automatically from:

```text
https://dl.oisd.nl/oisd_big_surge.list
```

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_big.srs
```

Recommended when maximum blocking is preferred over application compatibility.

---

## `oisd_small.srs`

Less aggressive advertising and malicious-domain blocking with better application compatibility.

Generated automatically from:

```text
https://dl.oisd.nl/oisd_small_surge.list
```

Release:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_small.srs
```

Recommended for:

- home routers;
- mobile devices;
- banking applications;
- government applications;
- environments where compatibility is more important than maximum filtering.

Only one OISD rule set should normally be enabled at a time.

For most home installations:

```text
oisd_small.srs
```

is recommended.

---

# OISD Allowlist

Before compilation, both OISD lists are filtered using:

```text
allowlist/oisd.txt
```

Domains in this file are removed from both:

```text
oisd_big.srs
oisd_small.srs
```

Current exclusions:

```text
appmetrica.yandex.net
uaas.yandex.ru
```

These domains were excluded after testing showed that blocking them prevented the Finuslugi iOS application from starting correctly.

To add another exception, append one domain per line:

```text
appmetrica.yandex.net
uaas.yandex.ru
example.com
```

Comments are supported:

```text
# Required by a banking application
example.com
```

GitHub Actions verifies that allowlisted domains are no longer present in the generated OISD files.

---

# GeoIP

## `ru.srs`

Russian IP ranges.

Official binary rule set maintained by Loyalsoldier:

```text
https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/srs/ru.srs
```

This file is downloaded directly by Podkop and is not generated by this repository.

GeoIP RU is useful for services that:

- use non-Russian domain zones;
- resolve to Russian IP addresses;
- use direct IP connections;
- rely on Russian CDN infrastructure.

Example:

```text
habr.com
→ 178.248.237.68
→ GeoIP RU
→ DIRECT
```

If such a domain must use PROXY, it must be added as an explicit higher-priority proxy domain.

---

# Podkop Proxy-Priority Patch

Podkop 0.7.21 may generate route rules in the following order:

```text
BLOCK
↓
DIRECT / GeoIP RU
↓
fully_routed_ips → PROXY
↓
user proxy domains
```

In that order, an explicit proxy domain can be intercepted by GeoIP RU before the user proxy rule is evaluated.

The helper script changes the order to:

```text
BLOCK
↓
user proxy domains → PROXY
↓
DIRECT / GeoIP RU
↓
fully_routed_ips → PROXY
```

The patch affects only domains explicitly configured in the main proxy section:

```text
podkop.main.user_domains_text
```

Example:

```text
habr.com
```

Other domains continue to use the standard routing logic.

---

## Install the patch

Download and run:

```sh
wget -O /root/patch-podkop-proxy-priority.sh \
  https://raw.githubusercontent.com/aydar-sharifulin/podkop-rules/main/scripts/patch-podkop-proxy-priority.sh

chmod +x /root/patch-podkop-proxy-priority.sh

/root/patch-podkop-proxy-priority.sh
```

The script:

- creates a backup of `/usr/bin/podkop`;
- checks that the expected Podkop structure is present;
- adds priority processing for the main proxy section;
- prevents duplicate processing of the same section;
- validates shell syntax with `sh -n`;
- restores the original file automatically if patching fails;
- restarts Podkop.

The patch is idempotent: running it again does not apply it twice.

After a Podkop package upgrade, `/usr/bin/podkop` may be replaced. In that case, run the patch script again.

---

## Verify the patch

Check that the proxy-domain rule appears before DIRECT:

```sh
podkop show_sing_box_config
```

Expected route order:

```text
block-oisd...
main-user-domains-ruleset → main-out
direct-... → direct-out
source_ip_cidr → main-out
```

For detailed testing, temporarily enable informational logging:

```sh
uci set podkop.settings.log_level='info'
uci commit podkop
podkop restart
```

Generate a request:

```sh
curl -I https://habr.com
```

Check the route:

```sh
logread -e sing-box | grep -i 'habr.com' | tail -10
```

The connection should use:

```text
outbound/main-out
```

Return to normal logging:

```sh
uci set podkop.settings.log_level='warn'
uci commit podkop
podkop restart
```

---

# Recommended Podkop Configuration

## Main proxy section

Explicit domains that must always use PROXY:

```text
habr.com
```

These domains are evaluated before DIRECT and GeoIP after applying the priority patch.

---

## Direct domain rule sets

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ru-direct.srs
```

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ip-checkers.srs
```

Optional community list:

```text
russia_outside
```

---

## Direct subnet rule set

```text
https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/srs/ru.srs
```

---

## Block rule set

Recommended:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_small.srs
```

Maximum filtering:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd_big.srs
```

---

# DNS Recommendation

During testing, Google DNS produced the most stable results.

Recommended configuration:

```text
DNS type: DoH
Main DNS: 8.8.8.8
Bootstrap DNS: 77.88.8.8 or 8.8.8.8
```

Quad9 produced intermittent errors in the tested environment:

```text
SERVFAIL
unexpected EOF
502 Bad Gateway
```

These errors affected banking applications, Apple services and other unrelated domains.

The preferred resolver should be selected based on actual stability in the local network rather than theoretical protocol performance.

---

# Automatic Build Process

GitHub Actions performs the following steps:

1. Checks out the repository.
2. Creates clean temporary build directories.
3. Copies the source `ru-direct.json`.
4. Downloads the latest external source lists.
5. Generates:
   - `ip-checkers.json`;
   - `oisd_big.json`;
   - `oisd_small.json`.
6. Applies `allowlist/oisd.txt`.
7. Verifies that OISD exclusions were removed.
8. Downloads `custom-proxy.list`.
9. Reads `allowlist/proxy-from-direct.txt`.
10. Combines external and local proxy exceptions.
11. Generates the final `ru-direct.json` logic:
    ```text
    DIRECT AND NOT(PROXY EXCEPTIONS)
    ```
12. Validates all generated JSON files.
13. Verifies minimum rule counts.
14. Downloads the required sing-box version.
15. Compiles the generated JSON files into binary `.srs` files.
16. Verifies the compiled files.
17. Publishes them in the `latest` GitHub Release.

The workflow runs:

- manually through `workflow_dispatch`;
- after relevant repository changes;
- once per day.

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
├── build_ruleset.py
└── patch-podkop-proxy-priority.sh

build/
└── rules/
    ├── ru-direct.json
    ├── ip-checkers.json
    ├── oisd_big.json
    └── oisd_small.json

output/
├── ru-direct.srs
├── ip-checkers.srs
├── oisd_big.srs
└── oisd_small.srs
```

The `build/` and `output/` directories are generated during GitHub Actions and do not need to be committed.

Recommended `.gitignore` entries:

```text
build/
output/
*.tar.gz
```

---

# Released Files

```text
ru-direct.srs
ip-checkers.srs
oisd_big.srs
oisd_small.srs
```

Release base URL:

```text
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/
```

---

# Update Rules on OpenWrt

Podkop performs list updates automatically according to its configured interval.

Manual update:

```sh
podkop list_update
```

On low-power routers, processing `ru.srs` may take several minutes after the download completes.

Successful completion:

```text
✅ Lists update completed successfully
```

Restart Podkop:

```sh
podkop restart
```

Clear the sing-box DNS, FakeIP and remote-rule cache:

```sh
podkop stop
rm -f /tmp/sing-box/cache.db
podkop start
```

A full OpenWrt reboot also clears `/tmp`:

```sh
reboot
```

---

# Troubleshooting

## Check overall status

```sh
podkop global_check
```

## Check sing-box status

```sh
podkop get_sing_box_status
```

## Check errors

```sh
logread -e sing-box | grep -E 'FATAL|ERROR|SERVFAIL|unexpected EOF'
```

## Check Podkop update completion

```sh
logread -e podkop | tail -50
```

## Check a rule set

Binary `.srs` files must be decompiled before using `rule-set match`:

```sh
sing-box rule-set decompile \
  --output /tmp/ruleset.json \
  /tmp/ruleset.srs

sing-box rule-set match \
  /tmp/ruleset.json \
  example.com
```

## Check GeoIP match

```sh
sing-box rule-set match \
  /tmp/ru-geoip.json \
  178.248.237.68
```

Exit code `0` means the address matched the rule set.

---

# Final Routing Model

```text
Private and local networks
→ bypass TProxy through nftables

OISD
→ BLOCK

Explicit proxy domains
→ PROXY

Russian and trusted domains
→ DIRECT

Russian IP ranges
→ DIRECT

Everything else
→ PROXY
```

This provides predictable routing while preserving compatibility with Russian banking, government and Apple services.
