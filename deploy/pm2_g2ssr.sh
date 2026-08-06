#!/usr/bin/env bash
# pm2_g2ssr.sh —— g2-ssr 的 PM2 公共逻辑（被 init/start/restart/stop/status 复用）
#
# 约定：
#   - 只用 /opt/sqlbot/g2-ssr/node_modules/.bin/pm2，不用全局 pm2
#   - 入口必须是绝对路径 app.js（禁止把目录当成 script）
#   - 清掉历史错误进程名 app / 错误 script 登记

SQLBOT_HOME="${SQLBOT_HOME:-/opt/sqlbot}"
G2SSR_HOME="${G2SSR_HOME:-${SQLBOT_HOME}/g2-ssr}"
G2SSR_APP_JS="${G2SSR_HOME}/app.js"
PM2_BIN="${G2SSR_HOME}/node_modules/.bin/pm2"
G2SSR_PM2_NAME="g2-ssr"

pm2_bin() {
    if [[ ! -x "${PM2_BIN}" ]]; then
        printf "\033[31m[sqlbot] ERROR:\033[0m 未找到本地 PM2：%s\n" "${PM2_BIN}" >&2
        return 1
    fi
    printf '%s\n' "${PM2_BIN}"
}

# 删除同目录下的历史错误登记（默认名 app、错误 script 指向目录等）
pm2_cleanup_stale_g2ssr() {
    local pm2
    pm2="$(pm2_bin)" || return 1
    # 旧进程名 app：早期用 pm2 start app.js 未指定 --name 时产生
    "${pm2}" delete app >/dev/null 2>&1 || true

    # 若已有 g2-ssr，但 script path 不是 app.js，删掉后重建
    if "${pm2}" describe "${G2SSR_PM2_NAME}" >/dev/null 2>&1; then
        local script_path
        script_path="$("${pm2}" jlist 2>/dev/null | python3 -c "
import sys, json
try:
    apps = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for a in apps:
    if a.get('name') == '${G2SSR_PM2_NAME}':
        print((a.get('pm2_env') or {}).get('pm_exec_path') or '')
        break
" 2>/dev/null || true)"
        if [[ -n "${script_path}" && "${script_path}" != "${G2SSR_APP_JS}" ]]; then
            printf "\033[33m[sqlbot] WARN:\033[0m g2-ssr script 异常（%s），重建为 %s\n" \
                "${script_path}" "${G2SSR_APP_JS}" >&2
            "${pm2}" delete "${G2SSR_PM2_NAME}" >/dev/null 2>&1 || true
        fi
    fi
}

pm2_stop_g2ssr() {
    local pm2
    pm2="$(pm2_bin)" || return 0
    "${pm2}" stop "${G2SSR_PM2_NAME}" >/dev/null 2>&1 || true
    "${pm2}" stop app >/dev/null 2>&1 || true
}

pm2_ensure_g2ssr() {
    local pm2
    pm2="$(pm2_bin)" || return 1
    [[ -f "${G2SSR_APP_JS}" ]] || {
        printf "\033[31m[sqlbot] ERROR:\033[0m 缺少 %s\n" "${G2SSR_APP_JS}" >&2
        return 1
    }

    pm2_cleanup_stale_g2ssr

    if "${pm2}" describe "${G2SSR_PM2_NAME}" >/dev/null 2>&1; then
        "${pm2}" restart "${G2SSR_PM2_NAME}" --update-env
    else
        "${pm2}" start "${G2SSR_APP_JS}" \
            --name "${G2SSR_PM2_NAME}" \
            --cwd "${G2SSR_HOME}"
    fi
    "${pm2}" save >/dev/null
}
