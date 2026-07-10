python3 scripts/build_ruleset.py \
    https://dl.oisd.nl/oisd_big_surge.list \
    rules/oisd.json

python3 scripts/build_ruleset.py \
    https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/rules/domains_geo_detect.list \
    rules/ip-checkers.json
