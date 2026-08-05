#!/usr/bin/env bash
# restart —— 重启服务
set -euo pipefail
info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
[[ $EUID -ne 0 ]] && { echo "请用 sudo 运行"; exit 1; }
PM2_BIN=/opt/sqlbot/g2-ssr/node_modules/.bin/pm2
[[ -x "${PM2_BIN}" ]] || { echo "未找到 ${PM2_BIN}"; exit 1; }
info "重启服务…"
systemctl restart sqlbot sqlbot-mcp
if "${PM2_BIN}" describe g2-ssr >/dev/null 2>&1; then
    "${PM2_BIN}" restart g2-ssr --update-env
else
    cd /opt/sqlbot/g2-ssr
    "${PM2_BIN}" start app.js --name g2-ssr
fi
"/opt/sqlbot/health.sh"
info "已重启"
