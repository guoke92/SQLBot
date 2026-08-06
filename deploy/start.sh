#!/usr/bin/env bash
# start —— 启动服务
set -euo pipefail
info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
die()   { printf "\033[31m[sqlbot] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }
[[ $EUID -ne 0 ]] && die "请用 sudo 运行"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/pm2_g2ssr.sh"

info "启动服务…"
systemctl start sqlbot sqlbot-mcp
pm2_ensure_g2ssr || die "g2-ssr 启动失败"
"/opt/sqlbot/health.sh"
info "已启动"
