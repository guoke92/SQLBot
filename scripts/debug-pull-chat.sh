#!/usr/bin/env bash
#
# 从远程服务器拉取对话数据（对话列表 + 每条问答记录 + 执行日志）
# 自动完成 xpack 加密登录，数据保存在 .debug-data/<chatId>/ 下
#
# 用法：
#   ./scripts/debug-pull-chat.sh            # 拉所有对话
#   ./scripts/debug-pull-chat.sh <chat_id>  # 拉指定对话
#
set -euo pipefail

# ── 配置 ────────────────────────────────────────────────────────────────────
BASE_URL="https://et-test.qhhrly.cn"
USERNAME="admin"
PASSWORD="Lls@123456"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${ROOT_DIR}/.debug-data"

info()  { printf "\033[32m[debug]\033[0m %s\n" "$*"; }
die()   { printf "\033[31m[debug] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }

command -v node >/dev/null 2>&1 || die "需要 Node.js"
command -v curl >/dev/null 2>&1 || die "需要 curl"
mkdir -p "${OUT_DIR}"

# ── 1. 用 Node.js 加载 xpack UMD 加密登录，拿 token ──────────────────────────
info "登录 ${BASE_URL} …"

LOGIN_JS="/tmp/sqlbot-debug-login.js"
cat > "${LOGIN_JS}" <<'JSEOF'
const https = require('https')
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { rejectUnauthorized: false }, (res) => {
      let d = ''; res.on('data', c => (d += c)); res.on('end', () => resolve(d)); res.on('error', reject)
    }).on('error', reject)
  })
}
function fetchJson(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url)
    const req = https.request({
      hostname: u.hostname, port: u.port || 443, path: u.pathname + u.search,
      method: opts.method || 'GET', headers: opts.headers || {}, rejectUnauthorized: false,
    }, (res) => {
      let d = ''; res.on('data', c => (d += c)); res.on('end', () => resolve({ status: res.statusCode, body: d }))
    })
    req.on('error', reject); if (opts.body) req.write(opts.body); req.end()
  })
}
;(async () => {
  const BASE = process.argv[2], USER = process.argv[3], PWD = process.argv[4]
  const script = await fetchUrl(BASE + '/xpack_static/license-generator.umd.js')
  const vm = require('vm')
  const ctx = {
    window: {}, navigator: { userAgent: 'node' }, console,
    TextEncoder: require('util').TextEncoder, TextDecoder: require('util').TextDecoder,
    atob: (s) => Buffer.from(s, 'base64').toString('binary'),
    btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
    fetch: async (url) => {
      const r = await fetchJson(url)
      return { ok: r.status < 400, json: () => JSON.parse(r.body), text: () => r.body }
    },
    Headers: class { constructor(h){this.h=h||{}} get(k){return (this.h||{})[k.toLowerCase()]} set(k,v){this.h=this.h||{};this.h[k.toLowerCase()]=v} },
  }
  ctx.self = ctx; ctx.globalThis = ctx
  vm.createContext(ctx); vm.runInContext(script, ctx)
  const runtime = ctx.LicenseGenerator
  if (!runtime) { console.error('xpack runtime 加载失败'); process.exit(1) }
  await runtime.init(BASE + '/api/v1')
  const encUser = runtime.sqlbotEncrypt(USER)
  const encPwd = runtime.sqlbotEncrypt(PWD)
  const resp = await fetchJson(BASE + '/api/v1/login/access-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(encUser)}&password=${encodeURIComponent(encPwd)}`,
  })
  if (resp.status !== 200) { console.error('登录失败:', resp.status, resp.body); process.exit(1) }
  process.stdout.write(JSON.parse(resp.body).data.access_token)
})().catch(e => { console.error('ERR:', e.message); process.exit(1) })
JSEOF

TOKEN=$(node "${LOGIN_JS}" "${BASE_URL}" "${USERNAME}" "${PASSWORD}") || die "登录失败"
rm -f "${LOGIN_JS}"
info "登录成功，token: ${TOKEN:0:20}..."

AUTH_HEADER="X-SQLBOT-TOKEN: Bearer ${TOKEN}"

# ── 2. 拉对话列表 ────────────────────────────────────────────────────────────
info "拉取对话列表…"
CHAT_LIST=$(curl -sf "${BASE_URL}/api/v1/chat/list" -H "${AUTH_HEADER}") || die "拉取对话列表失败"
echo "${CHAT_LIST}" | python3 -m json.tool > "${OUT_DIR}/chat_list.json"
info "对话列表已保存到 .debug-data/chat_list.json"

# ── 3. 拉每个对话详情 + 日志 ──────────────────────────────────────────────────
TARGET_CHAT_ID="${1:-}"

pull_chat() {
    local chat_id="$1"
    local chat_dir="${OUT_DIR}/${chat_id}"
    mkdir -p "${chat_dir}"

    info "拉取对话 ${chat_id} 详情…"
    local chat_resp
    chat_resp=$(curl -sf "${BASE_URL}/api/v1/chat/${chat_id}" -H "${AUTH_HEADER}" 2>/dev/null) || {
        echo "  对话 ${chat_id} 拉取失败，跳过"
        return
    }
    echo "${chat_resp}" | python3 -m json.tool > "${chat_dir}/chat_detail.json"

    # 提取 record id 列表
    local record_ids
    record_ids=$(echo "${chat_resp}" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', {})
records = data.get('records') or data.get('recordList') or []
for r in records:
    rid = r.get('id')
    if rid: print(rid)
" 2>/dev/null || echo "")

    if [[ -z "${record_ids}" ]]; then
        info "  对话 ${chat_id} 无问答记录"
        return
    fi

    for rid in ${record_ids}; do
        info "  拉取 record ${rid} 日志…"
        curl -sf "${BASE_URL}/api/v1/chat/record/${rid}/log" \
            -H "${AUTH_HEADER}" 2>/dev/null | python3 -m json.tool > "${chat_dir}/record_${rid}_log.json" 2>/dev/null || \
            echo '{"error": "拉取失败"}' > "${chat_dir}/record_${rid}_log.json"
    done

    # 生成摘要
    python3 -c "
import json, os
chat_dir = '${chat_dir}'
with open(os.path.join(chat_dir, 'chat_detail.json')) as f:
    data = json.load(f).get('data', {})
records = data.get('records') or data.get('recordList') or []
lines = [f'对话 {data.get(\"id\")} - {data.get(\"brief\",\"\")}', f'记录数: {len(records)}', '']
for r in records:
    rid = r.get('id','')
    q   = (r.get('question') or '')[:120]
    sql = (r.get('sql') or '')[:200]
    err = (r.get('error') or '')[:200]
    fin  = r.get('finish')
    lines.append(f'--- record {rid} ---')
    lines.append(f'  问题: {q}')
    if err:
        lines.append(f'  错误: {err}')
    else:
        lines.append(f'  SQL : {sql}')
    lines.append(f'  完成: {fin}')
    lines.append('')
with open(os.path.join(chat_dir, 'summary.txt'), 'w') as f:
    f.write('\n'.join(lines))
" 2>/dev/null
    info "  对话 ${chat_id} 完成 → .debug-data/${chat_id}/（detail + logs + summary.txt）"
}

if [[ -n "${TARGET_CHAT_ID}" ]]; then
    pull_chat "${TARGET_CHAT_ID}"
else
    CHAT_IDS=$(echo "${CHAT_LIST}" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for c in data:
    cid = c.get('id')
    if cid: print(cid)
" 2>/dev/null || echo "")

    if [[ -z "${CHAT_IDS}" ]]; then
        info "无对话记录"
        exit 0
    fi

    for CID in ${CHAT_IDS}; do
        pull_chat "${CID}"
    done
fi

echo
info "全部完成。数据在 .debug-data/"
echo "  对话列表：  .debug-data/chat_list.json"
echo "  某对话摘要：.debug-data/<chatId>/summary.txt"
