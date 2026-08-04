#!/usr/bin/env bash
# stop —— 停止服务
set -euo pipefail
info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
[[ $EUID -ne 0 ]] && { echo "请用 sudo 运行"; exit 1; }
PM2_BIN=/opt/sqlbot/g2-ssr/node_modules/.bin/pm2
info "停止服务…"
systemctl stop sqlbot sqlbot-mcp 2>/dev/null || true
if [[ -x "${PM2_BIN}" ]]; then
    "${PM2_BIN}" stop g2-ssr 2>/dev/null || true
fi
info "已停止"
