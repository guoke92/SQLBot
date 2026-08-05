#!/usr/bin/env bash
#
# init —— 停服 + 更新文件 + 增量同步依赖 + 安装配置 + 启动检查
#
# 用法（root）：
#   sudo ./init.sh                 # 自动找 /tmp 下最新的包
#   sudo ./init.sh xxx.tar.gz      # 指定包
#
set -euo pipefail

SQLBOT_HOME=/opt/sqlbot
APP_HOME=${SQLBOT_HOME}/app
G2SSR_HOME=${SQLBOT_HOME}/g2-ssr
DEPLOY_DIR=${SQLBOT_HOME}/deploy

info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
die()   { printf "\033[31m[sqlbot] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }

[[ $EUID -ne 0 ]] && die "请用 root 或 sudo 运行"
[[ $# -gt 1 ]] && die "用法：sudo ./init.sh [xxx.tar.gz]"

# 找包：优先参数，否则取 /tmp 下最新的
TARBALL="${1:-}"
if [[ -z "${TARBALL}" ]]; then
    TARBALL=$(ls -t /tmp/sqlbot-server-*.tar.gz 2>/dev/null | head -1)
    [[ -z "${TARBALL}" ]] && die "未找到包。用法：sudo ./init.sh [xxx.tar.gz]"
fi
[[ ! -f "${TARBALL}" ]] && die "包不存在：${TARBALL}"
info "使用包：${TARBALL}"

# 停服
info "停止服务…"
systemctl stop sqlbot sqlbot-mcp 2>/dev/null || true
OLD_PM2_BIN="${G2SSR_HOME}/node_modules/.bin/pm2"
if [[ -x "${OLD_PM2_BIN}" ]]; then
    "${OLD_PM2_BIN}" stop g2-ssr 2>/dev/null || true
fi

# 清理旧版本，但保留体积较大的运行环境和运行期数据。
# 新包解压后由 uv/npm 增量校验，依赖有变化时会自动更新。
if [[ -d "${SQLBOT_HOME}" ]]; then
    info "清理旧文件（保留 .venv、node_modules 和 data）…"
    find "${SQLBOT_HOME}" -mindepth 1 -maxdepth 1 \
        ! -name 'init.sh' ! -name 'app' ! -name 'g2-ssr' ! -name 'data' \
        -exec rm -rf -- {} +
    if [[ -d "${APP_HOME}" ]]; then
        find "${APP_HOME}" -mindepth 1 -maxdepth 1 ! -name '.venv' \
            -exec rm -rf -- {} +
    fi
    if [[ -d "${G2SSR_HOME}" ]]; then
        find "${G2SSR_HOME}" -mindepth 1 -maxdepth 1 ! -name 'node_modules' \
            -exec rm -rf -- {} +
    fi
fi

# 解压到 /opt（会创建/覆盖 sqlbot/，包括 init.sh）
info "解压新包…"
tar -xzf "${TARBALL}" -C /opt || die "解压失败"

chmod 600 "${SQLBOT_HOME}/.env" 2>/dev/null || true

# 保留现有环境后始终做增量同步：锁文件未变化时不会重新下载全部依赖。
command -v uv >/dev/null 2>&1 || die "未找到 uv，请先安装 uv"
info "同步后端依赖…"
cd "${APP_HOME}"
uv sync --frozen --no-dev --extra cpu

command -v npm >/dev/null 2>&1 || die "未找到 npm"
info "同步 g2-ssr 依赖…"
cd "${G2SSR_HOME}"
npm install --omit=dev

PM2_BIN="${G2SSR_HOME}/node_modules/.bin/pm2"
[[ -x "${PM2_BIN}" ]] || die "未找到 g2-ssr 本地 PM2：${PM2_BIN}"

info "安装 systemd 服务…"
cp -f "${DEPLOY_DIR}/sqlbot.service" /etc/systemd/system/sqlbot.service
cp -f "${DEPLOY_DIR}/sqlbot-mcp.service" /etc/systemd/system/sqlbot-mcp.service
systemctl daemon-reload
systemctl enable sqlbot sqlbot-mcp >/dev/null

# 保持现有 nginx 配置内容不变，仅安装并校验。
info "安装 nginx 配置…"
cp -f "${DEPLOY_DIR}/sqlbot.conf" /etc/nginx/conf.d/sqlbot.conf
nginx -t
systemctl reload nginx

info "启动服务…"
systemctl restart sqlbot sqlbot-mcp
if "${PM2_BIN}" describe g2-ssr >/dev/null 2>&1; then
    "${PM2_BIN}" restart g2-ssr --update-env
else
    cd "${G2SSR_HOME}"
    "${PM2_BIN}" start app.js --name g2-ssr
fi
"${PM2_BIN}" save >/dev/null

"${SQLBOT_HOME}/health.sh"

echo
info "部署完成"
