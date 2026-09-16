#!/usr/bin/env bash
#
# 通过远程 API 批量创建用户（幂等：账号已存在则跳过）。
#
# 用法：
#   ./scripts/batch_create_users.sh            # dry-run：只查是否已存在
#   ./scripts/batch_create_users.sh --apply    # 真正 POST 创建
#
# 环境变量（可覆盖默认）：
#   SQLBOT_DEBUG_BASE_URL   默认 https://et-test.qhhrly.cn
#   SQLBOT_DEBUG_USERNAME   默认 admin
#   SQLBOT_DEBUG_PASSWORD   默认 Lls@123456
#   SQLBOT_BATCH_OID        默认 7504090896279801856（产融平台）
#
set -euo pipefail

BASE_URL="${SQLBOT_DEBUG_BASE_URL:-https://et-test.qhhrly.cn}"
USERNAME="${SQLBOT_DEBUG_USERNAME:-admin}"
PASSWORD="${SQLBOT_DEBUG_PASSWORD:-Lls@123456}"
OID="${SQLBOT_BATCH_OID:-7504090896279801856}"

APPLY=0

info()  { printf "\033[32m[batch-user]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[batch-user] WARN:\033[0m %s\n" "$*" >&2; }
die()   { printf "\033[31m[batch-user] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }

usage() {
    cat <<'EOF'
用法：
  ./scripts/batch_create_users.sh
  ./scripts/batch_create_users.sh --apply

选项：
  --apply        真正调用 POST /api/v1/user；缺省只预览
  -h, --help     显示帮助

环境变量：SQLBOT_DEBUG_BASE_URL / USERNAME / PASSWORD / SQLBOT_BATCH_OID
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --apply) APPLY=1 ;;
        -h|--help) usage; exit 0 ;;
        -*) die "未知参数：$1（见 --help）" ;;
        *) die "多余参数：$1" ;;
    esac
    shift
done

command -v node >/dev/null 2>&1 || die "需要 Node.js"
command -v curl >/dev/null 2>&1 || die "需要 curl"
command -v python3 >/dev/null 2>&1 || die "需要 python3"

# ── 用户名单：中文名;邮箱（账号 = 邮箱 @ 前缀）──────────────────────────────
# 改名单只改这里即可
USER_LINES=$(cat <<'EOF'
蒙雄发;mengxiongfa@linklogis.com
曾刘刚;zengliugang@linklogis.com
陈凯文;chenkaiwen@linklogis.com
陈平福;chenpingfu@linklogis.com
陈淑华;chenshuhua@linklogis.com
崔宁宁;cuiningning@linklogis.com
范军伟;fanjunwei@linklogis.com
樊新新;fanxinxin@linklogis.com
黄丽玉;huangliyu@linklogis.com
林仰科;linyangke@linklogis.com
刘倍材;liubeicai@linklogis.com
刘宁;liuning@linklogis.com
李祝锋;lizhufeng@linklogis.com
欧阳鹏飞;ouyangpengfei@linklogis.com
彭绍斌;pengshaobin@linklogis.com
申志彬;shenzhibin@linklogis.com
王聪;wangcong@linklogis.com
王合庆;wangheqing@linklogis.com
吴东洋;wudongyang@linklogis.com
肖龙豪;xiaolonghao@linklogis.com
谢清泉;xieqingquan@linklogis.com
薛梦冉;xuemengran@linklogis.com
闫恺;yankai@linklogis.com
张剑;zhangjian@linklogis.com
钟若美;zhongruomei@linklogis.com
周霞;zhouxia@linklogis.com
EOF
)

# ── 1. xpack 登录拿 token ────────────────────────────────────────────────────
info "登录 ${BASE_URL} （用户 ${USERNAME}）…"

LOGIN_JS="$(mktemp /tmp/sqlbot-batch-login.XXXXXX.js)"
cleanup() { rm -f "${LOGIN_JS}"; }
trap cleanup EXIT

cat > "${LOGIN_JS}" <<'JSEOF'
const https = require('https')
const http = require('http')
function clientFor(url) {
  return url.startsWith('https') ? https : http
}
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    clientFor(url).get(url, { rejectUnauthorized: false }, (res) => {
      let d = ''; res.on('data', c => (d += c)); res.on('end', () => resolve(d)); res.on('error', reject)
    }).on('error', reject)
  })
}
function fetchJson(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url)
    const lib = clientFor(url)
    const req = lib.request({
      hostname: u.hostname, port: u.port || (u.protocol === 'https:' ? 443 : 80),
      path: u.pathname + u.search,
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
  const body = JSON.parse(resp.body)
  const token = body?.data?.access_token || body?.access_token
  if (!token) { console.error('登录响应无 token:', resp.body); process.exit(1) }
  process.stdout.write(token)
})().catch(e => { console.error('ERR:', e.message); process.exit(1) })
JSEOF

TOKEN=$(node "${LOGIN_JS}" "${BASE_URL}" "${USERNAME}" "${PASSWORD}") || die "登录失败"
info "登录成功，token: ${TOKEN:0:20}..."

AUTH_HEADER="X-SQLBOT-TOKEN: Bearer ${TOKEN}"

# ── 2. 批量创建 ──────────────────────────────────────────────────────────────
MODE="DRY-RUN"
[[ "${APPLY}" -eq 1 ]] && MODE="APPLY"
info "mode=${MODE}  base=${BASE_URL}  oid=${OID}"
echo "--------------------------------------------------------------------------------"

CREATED=0
SKIPPED=0
ERRORS=0

while IFS=';' read -r NAME EMAIL; do
    [[ -z "${NAME}" || -z "${EMAIL}" ]] && continue
    ACCOUNT="${EMAIL%%@*}"
    ACCOUNT="$(printf '%s' "${ACCOUNT}" | tr '[:upper:]' '[:lower:]')"

    # 查是否已存在
    ENC_KW=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${ACCOUNT}'))")
    EXIST_JSON=$(curl -sS -H "${AUTH_HEADER}" -H 'Accept: application/json' \
        "${BASE_URL}/api/v1/user/pager/1/50?keyword=${ENC_KW}" || true)
    EXIST_ID=$(python3 -c "
import json,sys
try:
    d=json.loads(sys.argv[1])
except Exception:
    sys.exit(0)
data=d.get('data') or {}
items=data.get('items') or data.get('records') or data.get('list') or []
acc=sys.argv[2].lower()
for it in items:
    if str(it.get('account','')).lower()==acc:
        print(it.get('id') or '')
        break
" "${EXIST_JSON}" "${ACCOUNT}" 2>/dev/null || true)

    if [[ -n "${EXIST_ID}" ]]; then
        printf '%-8s %-20s skip_exists id=%s\n' "${NAME}" "${ACCOUNT}" "${EXIST_ID}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    BODY=$(python3 -c "
import json
print(json.dumps({
  'account': '${ACCOUNT}',
  'name': '''${NAME}''',
  'email': '${EMAIL}',
  'oid': int('${OID}'),
  'status': 1,
  'oid_list': [int('${OID}')],
  'system_variables': [],
  'origin': 0,
}, ensure_ascii=False))
")

    if [[ "${APPLY}" -ne 1 ]]; then
        printf '%-8s %-20s would_create %s\n' "${NAME}" "${ACCOUNT}" "${BODY}"
        CREATED=$((CREATED + 1))
        continue
    fi

    RESP=$(curl -sS -w '\n%{http_code}' -X POST "${BASE_URL}/api/v1/user" \
        -H "${AUTH_HEADER}" \
        -H 'Content-Type: application/json' \
        -H 'Accept: application/json' \
        -d "${BODY}" || true)
    HTTP_CODE=$(printf '%s' "${RESP}" | tail -n1)
    RESP_BODY=$(printf '%s' "${RESP}" | sed '$d')

    RESULT=$(python3 -c "
import json,sys
code=sys.argv[1]
raw=sys.argv[2]
try:
    p=json.loads(raw) if raw else {}
except Exception:
    p={'msg': raw}
msg=str(p.get('msg') or p.get('detail') or p.get('message') or '')
biz=p.get('code')
ok = code in ('200','201') and biz in (0,200,'0','200',None)
low=msg.lower()
exists=any(k in low for k in ('exist','已存在','已经存在','duplicate')) or ('存在' in msg)
if ok:
    data=p.get('data') or {}
    uid=data.get('id')
    print(f'created id={uid}' if uid else f'created ({msg})')
elif exists:
    print(f'skip_exists ({msg})')
else:
    print(f'ERROR http={code} code={biz} {msg or raw[:160]}')
" "${HTTP_CODE}" "${RESP_BODY}")

    printf '%-8s %-20s %s\n' "${NAME}" "${ACCOUNT}" "${RESULT}"
    case "${RESULT}" in
        created*) CREATED=$((CREATED + 1)) ;;
        skip_*) SKIPPED=$((SKIPPED + 1)) ;;
        *) ERRORS=$((ERRORS + 1)) ;;
    esac
done <<< "${USER_LINES}"

echo "--------------------------------------------------------------------------------"
info "done: created/would_create=${CREATED} exists/skip=${SKIPPED} errors=${ERRORS}"
if [[ "${APPLY}" -ne 1 ]]; then
    info "加 --apply 才会真正 POST ${BASE_URL}/api/v1/user"
fi
info "默认密码由远端 DEFAULT_PWD 决定（与系统「重置密码」一致）"
