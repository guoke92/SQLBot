#!/usr/bin/env bash
#
# AI智能问数 —— 本机打包脚本
# 生成一个含「源码 + 构建产物 + 配置」的 tar.gz。
# 配置通配，不绑定具体 IP/域名。
#
# 用法：
#   ./scripts/pack-server.sh
#
set -euo pipefail

# macOS: 禁止 tar 生成 AppleDouble (._*) 文件，避免 Linux 解压后 Python glob 误读
export COPYFILE_DISABLE=1

# ── 路径解析 ────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "${SCRIPT_DIR}/../backend" && -d "${SCRIPT_DIR}/../frontend" ]]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
else
    ROOT_DIR="${SCRIPT_DIR%/scripts}"
fi

ENV_FILE="${ROOT_DIR}/.env"
DEPLOY_DIR="${ROOT_DIR}/deploy"
STAGE_DIR="${ROOT_DIR}/dist-pack"
PKG_DIR="${STAGE_DIR}/sqlbot"

info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[sqlbot] WARN:\033[0m %s\n" "$*" >&2; }
err()   { printf "\033[31m[sqlbot] ERROR:\033[0m %s\n" "$*" >&2; }
die()   { err "$*"; exit 1; }

[[ $# -gt 0 ]] && die "打包脚本不接受参数，请直接执行 ./package.sh"

[[ ! -f "${ENV_FILE}" ]] && die "未找到 ${ENV_FILE}"

# ── 从本地 .env 继承密钥类变量 ──────────────────────────────────────────────
info "从本地 .env 读取密钥…"
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

SECRET_KEY_VAL="${SECRET_KEY:-}"
POSTGRES_PASSWORD_VAL="${POSTGRES_PASSWORD:-}"
EMBEDDING_API_BASE_VAL="${EMBEDDING_API_BASE:-}"
EMBEDDING_API_KEY_VAL="${EMBEDDING_API_KEY:-}"
DEFAULT_EMBEDDING_MODEL_VAL="${DEFAULT_EMBEDDING_MODEL:-}"

[[ -z "${SECRET_KEY_VAL}" ]]       && die "本地 .env 缺少 SECRET_KEY"
[[ -z "${POSTGRES_PASSWORD_VAL}" ]] && die "本地 .env 缺少 POSTGRES_PASSWORD"

info "  EMBEDDING_PROVIDER    = openai"
info "  EMBEDDING_API_BASE    = ${EMBEDDING_API_BASE_VAL}"
info "  DEFAULT_EMBEDDING_MODEL= ${DEFAULT_EMBEDDING_MODEL_VAL}"
# ── 1. 构建前端 ──────────────────────────────────────────────────────────────
build_frontend() {
    info "构建前端（npm run build）…"
    cd "${ROOT_DIR}/frontend"
    if [[ ! -d node_modules ]]; then
        info "前端依赖未安装，先 npm install…"
        npm install
    fi
    npm run build
    [[ -d "${ROOT_DIR}/frontend/dist" ]] || die "前端构建失败，未生成 dist"
    info "前端构建完成"
}

# ── 2. 清理并重建暂存目录 ────────────────────────────────────────────────────
prepare_stage() {
    info "清理暂存目录…"
    rm -rf "${STAGE_DIR}"
    mkdir -p "${PKG_DIR}" \
             "${PKG_DIR}/deploy" \
             "${PKG_DIR}/frontend" \
             "${PKG_DIR}/data"/{excel,file,images,logs,models}
}

# ── 3. 暂存内容 ──────────────────────────────────────────────────────────────
# rsync 加 --exclude='._*' 防止 macOS AppleDouble 文件混入
stage_code() {
    info "暂存后端源码…"
    rsync -a --delete \
        --exclude='venv/' --exclude='.venv/' \
        --exclude='__pycache__/' --exclude='*.pyc' \
        --exclude='.pytest_cache/' --exclude='.mypy_cache/' \
        --exclude='.ruff_cache/' \
        --exclude='._*' \
        "${ROOT_DIR}/backend/" "${PKG_DIR}/app/"

    info "暂存前端构建产物…"
    rsync -a --delete \
        --exclude='._*' \
        "${ROOT_DIR}/frontend/dist/" "${PKG_DIR}/frontend/dist/"

    info "暂存 g2-ssr 源码（排除 node_modules）…"
    rsync -a --delete \
        --exclude='node_modules/' \
        --exclude='._*' \
        "${ROOT_DIR}/g2-ssr/" "${PKG_DIR}/g2-ssr/"

    info "暂存 deploy 脚本…"
    cp -f "${DEPLOY_DIR}"/*.sh "${PKG_DIR}/"
    chmod +x "${PKG_DIR}"/*.sh
}

# ── 4. 渲染配置 ──────────────────────────────────────────────────────────────
# 密钥类从本地 .env 填充；CORS/nginx 通配，不绑定 IP
render_configs() {
    info "渲染配置文件…"
    local tmpl out

    # .env.server -> .env
    tmpl="${DEPLOY_DIR}/envs/.env.server"
    out="${PKG_DIR}/.env"
    sed \
        -e "s|__SECRET_KEY__|${SECRET_KEY_VAL}|g" \
        -e "s|__POSTGRES_PASSWORD__|${POSTGRES_PASSWORD_VAL}|g" \
        -e "s|__EMBEDDING_API_BASE__|${EMBEDDING_API_BASE_VAL}|g" \
        -e "s|__EMBEDDING_API_KEY__|${EMBEDDING_API_KEY_VAL}|g" \
        -e "s|__DEFAULT_EMBEDDING_MODEL__|${DEFAULT_EMBEDDING_MODEL_VAL}|g" \
        "${tmpl}" > "${out}"
    chmod 600 "${out}"

    # systemd 服务（模板里已硬编码 root，直接拷到 deploy/）
    for tmpl in "${DEPLOY_DIR}/systemd/sqlbot.service" "${DEPLOY_DIR}/systemd/sqlbot-mcp.service"; do
        out="${PKG_DIR}/deploy/$(basename "${tmpl}")"
        cp -f "${tmpl}" "${out}"
    done

    # nginx 站点（通配 server_name _，直接拷到 deploy/）
    tmpl="${DEPLOY_DIR}/nginx/sqlbot.conf"
    out="${PKG_DIR}/deploy/sqlbot.conf"
    cp -f "${tmpl}" "${out}"
}

# ── 5. 打包 ──────────────────────────────────────────────────────────────────
make_tarball() {
    # 清除 macOS 扩展属性，避免 Linux 解压时报 LIBARCHIVE.xattr 警告
    if command -v xattr >/dev/null 2>&1; then
        info "清除 macOS 扩展属性…"
        xattr -cr "${STAGE_DIR}" 2>/dev/null || true
    fi

    # 二次保险：删掉所有 ._ AppleDouble 文件
    find "${STAGE_DIR}" -name '._*' -delete 2>/dev/null || true

    info "打包 tar.gz…"
    local ts; ts=$(date +%Y%m%d-%H%M%S)
    PACKAGE_PATH="${ROOT_DIR}/sqlbot-server-${ts}.tar.gz"
    tar -czf "${PACKAGE_PATH}" -C "${STAGE_DIR}" sqlbot
    info "打包完成：${PACKAGE_PATH} ($(du -h "${PACKAGE_PATH}" | cut -f1))"

    # 验证 tarball 里没有 ._ 文件
    local apple_count; apple_count=$(tar -tzf "${PACKAGE_PATH}" | grep -c '\._' || true)
    if [[ "${apple_count}" -gt 0 ]]; then
        warn "tarball 里仍有 ${apple_count} 个 ._ 文件！"
    else
        info "验证通过：tarball 无 AppleDouble (._*) 文件"
    fi
}

# ── 6. 输出后续指引 ──────────────────────────────────────────────────────────
print_guide() {
    local tarball="$1"
    echo
    echo "==================== 后续操作 ===================="
    echo "1) 手动上传到远程机 /tmp/："
    echo "   ${tarball}"
    echo
    echo "2) 远程机上（root）："
    echo "   sudo ./init.sh                # 解压、同步依赖、安装配置并启动"
    echo
    echo "   其他："
    echo "   sudo ./status.sh              # 看状态"
    echo "   sudo ./restart.sh             # 重启"
    echo "   sudo ./stop.sh                # 停止"
    echo "================================================"
}

# ── main ────────────────────────────────────────────────────────────────────
command -v rsync >/dev/null 2>&1 || die "本机需要 rsync（macOS 自带）"

PACKAGE_PATH=""
build_frontend
prepare_stage
stage_code
render_configs
make_tarball
print_guide "${PACKAGE_PATH}"
