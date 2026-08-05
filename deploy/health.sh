#!/usr/bin/env bash
# health —— 检查一次完整 SQLBot 服务链路
set -euo pipefail

info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
die()   { printf "\033[31m[sqlbot] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }

wait_http() {
    local name="$1"
    local url="$2"
    local accept_any="${3:-false}"
    local code
    for _ in {1..30}; do
        code=$(curl -sS -o /dev/null -w '%{http_code}' "${url}" 2>/dev/null || true)
        if [[ "${code}" =~ ^[23][0-9][0-9]$ ]] || \
            [[ "${accept_any}" == "true" && "${code}" != "000" && -n "${code}" ]]; then
            info "  ${name}: HTTP ${code}"
            return 0
        fi
        sleep 1
    done
    journalctl -u sqlbot -u sqlbot-mcp --no-pager -n 30 >&2 || true
    die "${name} 健康检查失败：${url}"
}

info "检查服务…"
wait_http "后端/xpack" "http://127.0.0.1:8000/xpack_static/license-generator.umd.js"
wait_http "MCP" "http://127.0.0.1:8001/" true
wait_http "g2-ssr" "http://127.0.0.1:3000/"
wait_http "前端" "http://127.0.0.1:3001/"
