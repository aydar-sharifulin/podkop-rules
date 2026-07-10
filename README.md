# Podkop Rule Sets

Custom rule sets for Podkop / sing-box.

These rule sets are automatically built by GitHub Actions and published as GitHub Releases.

---

## Direct (Domain)

### ru-direct.srs

Russian domains that should always bypass the proxy.

```
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ru-direct.srs
```

Examples:

- .ru
- .рф
- .su
- manually added domains

---

### ip-checkers.srs

IP detection and geolocation services.

Generated automatically from:

https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/rules/domains_geo_detect.list

Release:

```
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/ip-checkers.srs
```

---

## Block

### oisd.srs

Advertisement, tracking and malicious domains.

Generated automatically from:

https://dl.oisd.nl/oisd_big_surge.list

Release:

```
https://github.com/aydar-sharifulin/podkop-rules/releases/download/latest/oisd.srs
```

---

## GeoIP

Russian IP ranges.

Official binary rule set by Loyalsoldier.

```
https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/srs/ru.srs
```

This rule set is downloaded directly by Podkop and is **not** built by this repository.

---

## Automatic Updates

GitHub Actions automatically:

- downloads the latest external rule lists;
- converts them to sing-box JSON rule sets;
- validates JSON;
- compiles all `rules/*.json` into `.srs`;
- publishes the latest GitHub Release.

Podkop downloads updated rule sets once per day.

---

## Repository Structure

```
rules/
    ru-direct.json
    ip-checkers.json
    oisd.json

scripts/
    build_ruleset.py

output/
    *.srs
```

---

## Routing Policy

| Rule Set | Action |
|----------|--------|
| ru-direct.srs | DIRECT |
| ip-checkers.srs | DIRECT |
| ru.srs (GeoIP RU) | DIRECT |
| oisd.srs | BLOCK |
| everything else | PROXY |
