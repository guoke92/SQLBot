#!/usr/bin/env bash
# stop —— 停止服务
set -euo pipefail
info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
[[ $EUID -ne 0 ]] && { echo "请用 sudo 运行"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
if [[ -f "${SCRIPT_DIR}/pm2_g2ssr.sh" ]]; then
    source "${SCRIPT_DIR}/pm2_g2ssr.sh"
fi

info "停止服务…"
systemctl stop sqlbot sqlbot-mcp 2>/dev/null || true
if declare -F pm2_stop_g2ssr >/dev/null 2>&1; then
    pm2_stop_g2ssr
else
    PM2_BIN=/opt/sqlbot/g2-ssr/node_modules/.bin/pm2
    if [[ -x "${PM2_BIN}" ]]; then
        "${PM2_BIN}" stop g2-ssr 2>/dev/null || true
        "${PM2_BIN}" stop app 2>/dev/null || true
    fi
fi
info "已停止"
