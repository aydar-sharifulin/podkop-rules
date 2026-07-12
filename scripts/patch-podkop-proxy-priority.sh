#!/bin/ash

set -eu

TARGET="/usr/bin/podkop"
MARKER="PODKOP_PRIORITY_PROXY_PATCH"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="${TARGET}.bak-${TIMESTAMP}"
TMP="${TARGET}.tmp-${TIMESTAMP}"

restore_backup() {
    echo "Ошибка. Восстанавливаю исходный файл..."
    cp "$BACKUP" "$TARGET"
    chmod 0755 "$TARGET"
    rm -f "$TMP"
}

if [ ! -f "$TARGET" ]; then
    echo "Файл не найден: $TARGET"
    exit 1
fi

if grep -q "$MARKER" "$TARGET"; then
    echo "Патч уже установлен."
    exit 0
fi

echo "Проверяю структуру $TARGET..."

required_patterns="
sing_box_configure_route() {
    configure_common_reject_route_rule
    configure_common_direct_route_rule
    config_foreach configure_routing_for_section_lists \"section\"
configure_routing_for_section_lists() {
"

echo "$required_patterns" | while IFS= read -r pattern; do
    [ -z "$pattern" ] && continue

    if ! grep -Fq "$pattern" "$TARGET"; then
        echo "Не найден ожидаемый фрагмент:"
        echo "  $pattern"
        echo "Версия Podkop может отличаться. Файл не изменён."
        exit 1
    fi
done

echo "Создаю резервную копию:"
echo "  $BACKUP"

cp "$TARGET" "$BACKUP"

awk '
BEGIN {
    inserted_priority = 0
    replaced_foreach = 0
    inserted_helper = 0
}

# После общего BLOCK вставляем раннюю обработку основной
# proxy-секции. configure_common_direct_route_rule,
# находящийся на следующей строке, остаётся на месте.
$0 ~ /^[[:space:]]*configure_common_reject_route_rule[[:space:]]*$/ {
    print
    print ""
    print "    # PODKOP_PRIORITY_PROXY_PATCH"
    print "    # Proxy/VPN rules of the main outbound must be evaluated"
    print "    # before DIRECT domain lists and GeoIP rules."
    print "    configure_routing_for_section_lists \"$first_outbound_section\""
    inserted_priority = 1
    next
}

# В конце не обрабатываем main повторно.
$0 ~ /^[[:space:]]*config_foreach configure_routing_for_section_lists "section"[[:space:]]*$/ {
    print "    config_foreach configure_routing_for_remaining_sections \"section\" \"$first_outbound_section\""
    replaced_foreach = 1
    next
}

# Добавляем вспомогательную функцию перед исходной
# configure_routing_for_section_lists().
$0 ~ /^configure_routing_for_section_lists\(\)[[:space:]]*\{/ {
    print "configure_routing_for_remaining_sections() {"
    print "    local section=\"$1\""
    print "    local priority_section=\"$2\""
    print ""
    print "    # Main proxy section was already processed before DIRECT."
    print "    [ \"$section\" = \"$priority_section\" ] && return 0"
    print ""
    print "    configure_routing_for_section_lists \"$section\""
    print "}"
    print ""
    inserted_helper = 1
    print
    next
}

{
    print
}

END {
    if (!inserted_priority) {
        print "ERROR: priority insertion point was not found" > "/dev/stderr"
        exit 10
    }

    if (!replaced_foreach) {
        print "ERROR: config_foreach replacement point was not found" > "/dev/stderr"
        exit 11
    }

    if (!inserted_helper) {
        print "ERROR: helper insertion point was not found" > "/dev/stderr"
        exit 12
    }
}
' "$TARGET" > "$TMP" || {
    restore_backup
    exit 1
}

chmod 0755 "$TMP"

echo "Проверяю синтаксис..."

if ! sh -n "$TMP"; then
    restore_backup
    echo "Проверка синтаксиса не пройдена."
    exit 1
fi

mv "$TMP" "$TARGET"
chmod 0755 "$TARGET"

echo "Патч установлен."
echo "Проверяю наличие изменений..."

if ! grep -q "$MARKER" "$TARGET"; then
    restore_backup
    echo "Маркер патча не найден после установки."
    exit 1
fi

if ! sh -n "$TARGET"; then
    restore_backup
    echo "Итоговый файл не прошёл проверку синтаксиса."
    exit 1
fi

echo "Перезапускаю Podkop..."

if ! podkop restart; then
    restore_backup
    echo "Podkop не смог перезапуститься."
    echo "Восстановлена резервная копия."
    podkop restart || true
    exit 1
fi

echo
echo "Готово."
echo "Резервная копия:"
echo "  $BACKUP"
echo
echo "Ожидаемый порядок:"
echo "  1. BLOCK"
echo "  2. main-user-domains-ruleset -> PROXY"
echo "  3. DIRECT domains + GeoIP RU"
echo "  4. fully_routed_ips -> PROXY"
