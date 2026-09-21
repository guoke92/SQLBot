#!/usr/bin/env bash
#
# AI智能问数 —— 本机打包脚本
# 生成一个含「源码 + 构建产物 + 配置 + wiki 语料」的 tar.gz。
# 配置通配，不绑定具体 IP/域名。
# wiki 语料位于 docs/wiki/v3/（L1 draft；运行时召回走 DB，本地仅供导入/打包）。
# 历史 wiki-pages* / substrate 等已迁 .tmp/。
#
# 默认自动判断：
#   - pnpm-lock.yaml 内容指纹未变 → 跳过 install
#   - 前端构建输入指纹未变且 dist 可用 → 跳过 build
#
# 用法：
#   ./package.sh
#   ./package.sh --force-install
#   ./package.sh --force-build
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
FRONTEND_DIR="${ROOT_DIR}/frontend"
LOCKFILE="${FRONTEND_DIR}/pnpm-lock.yaml"
LOCK_STAMP="${FRONTEND_DIR}/node_modules/.pnpm-lock.sha256"
BUILD_STAMP="${FRONTEND_DIR}/dist/.build-inputs.sha256"

FORCE_INSTALL=0
FORCE_BUILD=0

info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[sqlbot] WARN:\033[0m %s\n" "$*" >&2; }
err()   { printf "\033[31m[sqlbot] ERROR:\033[0m %s\n" "$*" >&2; }
die()   { err "$*"; exit 1; }

usage() {
    cat <<'EOF'
用法：
  ./package.sh
  ./package.sh --force-install
  ./package.sh --force-build

默认会根据指纹自动跳过未变化的 pnpm install / 前端 build。

选项：
  --force-install    强制重新 pnpm install
  --force-build      强制重新构建前端
  -h, --help         显示帮助
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force-install) FORCE_INSTALL=1 ;;
        --force-build) FORCE_BUILD=1 ;;
        --skip-build)
            die "--skip-build 已移除：默认会自动跳过未变化的 build；如需强制重建用 --force-build"
            ;;
        -h|--help) usage; exit 0 ;;
        *) die "未知参数：$1（见 ./package.sh --help）" ;;
    esac
    shift
done

[[ ! -f "${ENV_FILE}" ]] && die "未找到 ${ENV_FILE}"

file_sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

sha256_stdin() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum | awk '{print $1}'
    else
        shasum -a 256 | awk '{print $1}'
    fi
}

# 文件身份：size + mtime（比整文件内容哈希快得多；误判时最多多 build 一次）
file_stat_id() {
    if stat -f '%z %m' "$1" >/dev/null 2>&1; then
        stat -f '%z %m' "$1"
    else
        stat -c '%s %Y' "$1"
    fi
}

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
lockfile_unchanged() {
    [[ -f "${LOCKFILE}" ]] || return 1
    [[ -d "${FRONTEND_DIR}/node_modules/.pnpm" ]] || return 1
    [[ -f "${LOCK_STAMP}" ]] || return 1
    local current cached
    current="$(file_sha256 "${LOCKFILE}")"
    cached="$(tr -d '[:space:]' < "${LOCK_STAMP}" || true)"
    [[ -n "${cached}" && "${current}" == "${cached}" ]]
}

# 影响 Vite 产物的输入：配置 + src/public（不含 node_modules）
list_frontend_build_inputs() {
    local f
    for f in \
        package.json \
        pnpm-lock.yaml \
        index.html \
        embedded.html \
        vite.config.ts \
        postcss.config.js \
        tsconfig.json \
        tsconfig.app.json \
        tsconfig.node.json \
        .env \
        .env.production \
        .env.local
    do
        [[ -f "${FRONTEND_DIR}/${f}" ]] && printf '%s\n' "${f}"
    done
    (
        cd "${FRONTEND_DIR}"
        find src public -type f ! -name '._*' 2>/dev/null || true
    )
}

frontend_build_fingerprint() {
    (
        cd "${FRONTEND_DIR}"
        list_frontend_build_inputs | LC_ALL=C sort -u | while IFS= read -r f; do
            [[ -f "${f}" ]] || continue
            printf '%s %s\n' "$(file_stat_id "${f}")" "${f}"
        done
    ) | sha256_stdin
}

build_inputs_unchanged() {
    [[ -d "${FRONTEND_DIR}/dist" ]] || return 1
    [[ -f "${BUILD_STAMP}" ]] || return 1
    # dist 至少应有入口产物，避免空目录误判
    [[ -f "${FRONTEND_DIR}/dist/index.html" ]] || return 1
    local current cached
    current="$(frontend_build_fingerprint)"
    cached="$(tr -d '[:space:]' < "${BUILD_STAMP}" || true)"
    [[ -n "${cached}" && "${current}" == "${cached}" ]]
}

# 返回 0 = 执行了 install；1 = 跳过
install_frontend_deps() {
    command -v pnpm >/dev/null 2>&1 || die "本机需要 pnpm"
    [[ -f "${LOCKFILE}" ]] || die "未找到 ${LOCKFILE}"

    if [[ "${FORCE_INSTALL}" -eq 0 ]] && lockfile_unchanged; then
        info "pnpm-lock.yaml 未变，跳过 pnpm install"
        return 1
    fi

    info "安装前端依赖（pnpm frozen lockfile）…"
    cd "${FRONTEND_DIR}"
    CI=true pnpm install --frozen-lockfile
    mkdir -p "${FRONTEND_DIR}/node_modules"
    file_sha256 "${LOCKFILE}" > "${LOCK_STAMP}"
    info "前端依赖安装完成"
    return 0
}

build_frontend() {
    local did_install=0
    if install_frontend_deps; then
        did_install=1
    fi

    if [[ "${FORCE_BUILD}" -eq 0 && "${did_install}" -eq 0 ]] && build_inputs_unchanged; then
        info "前端输入未变，跳过 build，复用 frontend/dist"
        return 0
    fi

    if [[ "${did_install}" -eq 1 ]]; then
        info "依赖已更新，需要重新 build"
    elif [[ "${FORCE_BUILD}" -eq 1 ]]; then
        info "强制重新构建前端…"
    else
        info "前端输入有变化，构建前端…"
    fi

    cd "${FRONTEND_DIR}"
    CI=true pnpm build
    [[ -f "${FRONTEND_DIR}/dist/index.html" ]] || die "前端构建失败，未生成 dist/index.html"
    frontend_build_fingerprint > "${BUILD_STAMP}"
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
        --exclude='.claude/' \
        --exclude='._*' \
        "${ROOT_DIR}/backend/" "${PKG_DIR}/app/"

    info "暂存前端构建产物…"
    rsync -a --delete \
        --exclude='._*' \
        --exclude='.build-inputs.sha256' \
        "${FRONTEND_DIR}/dist/" "${PKG_DIR}/frontend/dist/"

    info "暂存 g2-ssr 源码（排除 node_modules）…"
    rsync -a --delete \
        --exclude='node_modules/' \
        --exclude='._*' \
        "${ROOT_DIR}/g2-ssr/" "${PKG_DIR}/g2-ssr/"

    info "暂存 deploy 脚本…"
    cp -f "${DEPLOY_DIR}"/*.sh "${PKG_DIR}/"
    chmod +x "${PKG_DIR}"/*.sh

    # Wiki 语料：部署后可供管理端导入；运行时召回使用 DB corpus。
    # 现行工作区 docs/wiki/v3（L1 draft）+ req-index（文档源，可选）。
    local wiki_v3="${ROOT_DIR}/docs/wiki/v3"
    if [[ -d "${wiki_v3}" ]]; then
        info "暂存 wiki 语料（docs/wiki/v3）…"
        mkdir -p "${PKG_DIR}/docs/wiki"
        rsync -a --delete \
            --exclude='.obsidian/' \
            --exclude='.runs/' \
            --exclude='._*' \
            --exclude='__pycache__/' \
            "${wiki_v3}/" "${PKG_DIR}/docs/wiki/v3/"
    else
        warn "未找到 ${wiki_v3}，跳过 wiki 语料打包"
    fi
    local req_index="${ROOT_DIR}/docs/wiki-knowledge/pplatform/req-index"
    if [[ -d "${req_index}" ]]; then
        info "暂存 wiki 文档源（req-index）…"
        mkdir -p "${PKG_DIR}/docs/wiki-knowledge/pplatform"
        rsync -a --delete \
            --exclude='.obsidian/' \
            --exclude='._*' \
            "${req_index}/" "${PKG_DIR}/docs/wiki-knowledge/pplatform/req-index/"
    fi
    if [[ -f "${ROOT_DIR}/docs/wiki-knowledge/README.md" ]]; then
        mkdir -p "${PKG_DIR}/docs/wiki-knowledge"
        cp -f "${ROOT_DIR}/docs/wiki-knowledge/README.md" "${PKG_DIR}/docs/wiki-knowledge/README.md"
    fi
}

# ── 4. 渲染配置 ──────────────────────────────────────────────────────────────
# 密钥类从本地 .env 填充；CORS/nginx 通配，不绑定 IP
render_configs() {
    info "渲染配置文件…"
    local tmpl out

    # sed replacement 中的反斜杠、& 和分隔符必须转义，否则会破坏 .env。
    escape_sed_replacement() {
        printf '%s' "$1" | sed 's/[\\&|]/\\&/g'
    }

    local secret_key_escaped postgres_password_escaped
    local embedding_api_base_escaped embedding_api_key_escaped
    local default_embedding_model_escaped
    secret_key_escaped=$(escape_sed_replacement "${SECRET_KEY_VAL}")
    postgres_password_escaped=$(escape_sed_replacement "${POSTGRES_PASSWORD_VAL}")
    embedding_api_base_escaped=$(escape_sed_replacement "${EMBEDDING_API_BASE_VAL}")
    embedding_api_key_escaped=$(escape_sed_replacement "${EMBEDDING_API_KEY_VAL}")
    default_embedding_model_escaped=$(
        escape_sed_replacement "${DEFAULT_EMBEDDING_MODEL_VAL}"
    )

    # .env.server -> .env
    tmpl="${DEPLOY_DIR}/envs/.env.server"
    out="${PKG_DIR}/.env"
    sed \
        -e "s|__SECRET_KEY__|${secret_key_escaped}|g" \
        -e "s|__POSTGRES_PASSWORD__|${postgres_password_escaped}|g" \
        -e "s|__EMBEDDING_API_BASE__|${embedding_api_base_escaped}|g" \
        -e "s|__EMBEDDING_API_KEY__|${embedding_api_key_escaped}|g" \
        -e "s|__DEFAULT_EMBEDDING_MODEL__|${default_embedding_model_escaped}|g" \
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

# ── 5. 部署就绪校验（与 init.sh 契约对齐）────────────────────────────────────
# 自动跳过 install/build 时仍必须保证产物能被远端 init.sh 解压并启动。
verify_stage_for_init() {
    info "校验打包产物是否满足 init.sh 部署要求…"
    local missing=0
    local path
    local required_paths=(
        "${PKG_DIR}/.env"
        "${PKG_DIR}/init.sh"
        "${PKG_DIR}/health.sh"
        "${PKG_DIR}/start.sh"
        "${PKG_DIR}/app/main.py"
        "${PKG_DIR}/app/pyproject.toml"
        "${PKG_DIR}/app/uv.lock"
        "${PKG_DIR}/app/graphs/current/chat.yaml"
        "${PKG_DIR}/frontend/dist/index.html"
        "${PKG_DIR}/g2-ssr/app.js"
        "${PKG_DIR}/g2-ssr/package.json"
        "${PKG_DIR}/g2-ssr/package-lock.json"
        "${PKG_DIR}/deploy/sqlbot.service"
        "${PKG_DIR}/deploy/sqlbot-mcp.service"
        "${PKG_DIR}/deploy/sqlbot.conf"
        "${PKG_DIR}/docs/wiki/v3"
    )

    for path in "${required_paths[@]}"; do
        if [[ ! -e "${path}" ]]; then
            err "缺少：${path#"${PKG_DIR}"/}"
            missing=1
        fi
    done

    if [[ ! -d "${PKG_DIR}/frontend/dist/assets" ]]; then
        err "缺少 frontend/dist/assets（可能复用了不完整的 dist，请 ./package.sh --force-build）"
        missing=1
    fi

    if [[ ! -x "${PKG_DIR}/init.sh" || ! -x "${PKG_DIR}/health.sh" ]]; then
        err "init.sh / health.sh 不可执行"
        missing=1
    fi

    if grep -qE '__[A-Z0-9_]+__' "${PKG_DIR}/.env"; then
        err ".env 仍有未替换占位符："
        grep -E '__[A-Z0-9_]+__' "${PKG_DIR}/.env" >&2 || true
        missing=1
    fi

    # 本地打包戳不应进入部署包
    if [[ -e "${PKG_DIR}/frontend/dist/.build-inputs.sha256" ]]; then
        err "产物中不应包含 .build-inputs.sha256"
        missing=1
    fi

    [[ "${missing}" -eq 0 ]] || die "打包校验失败，已中止（避免远端 init.sh 部署踩坑）"
    info "打包产物校验通过"
}

# ── 6. 打包 ──────────────────────────────────────────────────────────────────
make_tarball() {
    # COPYFILE_DISABLE + rsync/find 排除 ._*; 不再整树 xattr -cr（macOS 上很慢）
    find "${STAGE_DIR}" -name '._*' -delete 2>/dev/null || true

    info "打包 tar.gz…"
    local ts; ts=$(date +%Y%m%d-%H%M%S)
    PACKAGE_PATH="${ROOT_DIR}/sqlbot-server-${ts}.tar.gz"
    # 优先 pigz 多核压缩；否则用较快的 gzip 级别
    if command -v pigz >/dev/null 2>&1; then
        tar -cf - -C "${STAGE_DIR}" sqlbot | pigz -1 > "${PACKAGE_PATH}"
    else
        GZIP=-1 tar -czf "${PACKAGE_PATH}" -C "${STAGE_DIR}" sqlbot
    fi
    info "打包完成：${PACKAGE_PATH} ($(du -h "${PACKAGE_PATH}" | cut -f1))"

    # 在暂存目录校验即可，避免再完整列出 tarball
    local apple_count
    apple_count=$(find "${STAGE_DIR}" -name '._*' 2>/dev/null | wc -l | tr -d ' ')
    if [[ "${apple_count}" -gt 0 ]]; then
        warn "暂存目录仍有 ${apple_count} 个 ._ 文件！"
    else
        info "验证通过：暂存目录无 AppleDouble (._*) 文件"
    fi
}

# ── 7. 输出后续指引 ──────────────────────────────────────────────────────────
print_guide() {
    local tarball="$1"
    local name; name="$(basename "${tarball}")"
    echo
    echo "==================== 后续操作 ===================="
    echo "1) 上传到远程机 /tmp/${name}"
    echo
    echo "2) 远程机上（root）执行 init.sh："
    echo "   # 已有旧版本时："
    echo "   sudo /opt/sqlbot/init.sh /tmp/${name}"
    echo
    echo "   # 首次安装（先抽出包内 init.sh）："
    echo "   sudo tar -xzf /tmp/${name} -C /tmp sqlbot/init.sh"
    echo "   sudo /tmp/sqlbot/init.sh /tmp/${name}"
    echo
    echo "   init.sh 会：解压到 /opt/sqlbot → uv sync → npm install g2-ssr"
    echo "               → 安装 systemd/nginx → 启动并 health 检查"
    echo
    echo "   其他："
    echo "   sudo /opt/sqlbot/status.sh"
    echo "   sudo /opt/sqlbot/restart.sh"
    echo "   sudo /opt/sqlbot/stop.sh"
    echo "================================================"
}

# ── main ────────────────────────────────────────────────────────────────────
command -v rsync >/dev/null 2>&1 || die "本机需要 rsync（macOS 自带）"

PACKAGE_PATH=""
build_frontend
prepare_stage
stage_code
render_configs
verify_stage_for_init
make_tarball
print_guide "${PACKAGE_PATH}"
