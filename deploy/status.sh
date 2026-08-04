#!/usr/bin/env bash
# status —— 查看状态
set -euo pipefail
echo
echo "=== systemd ==="
systemctl status sqlbot sqlbot-mcp --no-pager -l 2>/dev/null | grep -E "Active:|●" || true
echo
echo "=== PM2 ==="
PM2_BIN=/opt/sqlbot/g2-ssr/node_modules/.bin/pm2
if [[ -x "${PM2_BIN}" ]]; then
    "${PM2_BIN}" status 2>/dev/null || true
else
    echo "未找到 ${PM2_BIN}"
fi
echo
echo "=== 端口 ==="
ss -lntp 2>/dev/null | grep -E '8000|8001|3000|3001|5432' || true
echo
echo "=== 健康检查 ==="
curl -s -o /dev/null -w "  后端    : HTTP %{http_code}\n" http://127.0.0.1:8000/api/v1/system/license 2>/dev/null || echo "  后端    : 不可达"
curl -s -o /dev/null -w "  MCP     : HTTP %{http_code}\n" http://127.0.0.1:8001/ 2>/dev/null || echo "  MCP     : 不可达"
curl -s -o /dev/null -w "  g2-ssr  : HTTP %{http_code}\n" http://127.0.0.1:3000/ 2>/dev/null || echo "  g2-ssr  : 不可达"
curl -s -o /dev/null -w "  前端    : HTTP %{http_code}\n" http://127.0.0.1:3001/ 2>/dev/null || echo "  前端    : 不可达"
echo
