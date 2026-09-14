#!/usr/bin/env bash
#
# 从远程服务拉取目标工作空间的对话与反馈。
#
# 调用 GET /api/v1/chat/workspace/export（需 admin / 工作空间管理员）。
# 登录方式与 scripts/debug-pull-chat.sh 相同。
#
# 用法：
#   ./scripts/pull-workspace-chats.sh --oid 1
#   ./scripts/pull-workspace-chats.sh --oid 1 --feedback-only
#   ./scripts/pull-workspace-chats.sh --list-workspaces
#
# 环境变量（可覆盖默认）：
#   SQLBOT_DEBUG_BASE_URL   默认 https://et-test.qhhrly.cn
#   SQLBOT_DEBUG_USERNAME   默认 admin
#   SQLBOT_DEBUG_PASSWORD   默认 Lls@123456
#
set -euo pipefail

BASE_URL="${SQLBOT_DEBUG_BASE_URL:-https://et-test.qhhrly.cn}"
USERNAME="${SQLBOT_DEBUG_USERNAME:-admin}"
PASSWORD="${SQLBOT_DEBUG_PASSWORD:-Lls@123456}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_ROOT="${ROOT_DIR}/.debug-data"

LIST_WS=0
FEEDBACK_ONLY=0
INCLUDE_SQL=1
TARGET_OID=""

info()  { printf "\033[32m[export]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[export] WARN:\033[0m %s\n" "$*" >&2; }
die()   { printf "\033[31m[export] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }

usage() {
    cat <<'EOF'
用法：
  ./scripts/pull-workspace-chats.sh --oid <workspace_id>
  ./scripts/pull-workspace-chats.sh --oid <workspace_id> --feedback-only
  ./scripts/pull-workspace-chats.sh --list-workspaces

选项：
  --oid ID           目标工作空间 ID（admin 可指定任意空间；ws_admin 仅当前空间）
  --feedback-only    只导出有「有帮助/没帮助」的回合
  --no-sql           不带 SQL 文本
  --list-workspaces  列出工作空间后退出
  -h, --help         显示帮助

环境变量：SQLBOT_DEBUG_BASE_URL / USERNAME / PASSWORD
产出：.debug-data/workspace-<oid>/export.json、FEEDBACK.md、chats.csv
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --oid)
            [[ $# -ge 2 ]] || die "--oid 需要参数"
            TARGET_OID="$2"
            shift
            ;;
        --feedback-only) FEEDBACK_ONLY=1 ;;
        --no-sql) INCLUDE_SQL=0 ;;
        --list-workspaces) LIST_WS=1 ;;
        -h|--help) usage; exit 0 ;;
        -*)
            die "未知参数：$1（见 --help）"
            ;;
        *)
            die "多余参数：$1（工作空间请用 --oid）"
            ;;
    esac
    shift
done

command -v node >/dev/null 2>&1 || die "需要 Node.js"
command -v curl >/dev/null 2>&1 || die "需要 curl"
command -v python3 >/dev/null 2>&1 || die "需要 python3"
mkdir -p "${OUT_ROOT}"

info "登录 ${BASE_URL} …"

LOGIN_JS="$(mktemp /tmp/sqlbot-ws-export-login.XXXXXX.js)"
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

curl_json() {
    local out="$1"
    local url="$2"
    local code
    code=$(curl -sS -o "${out}.tmp" -w '%{http_code}' \
        -H "${AUTH_HEADER}" \
        -H 'Accept: application/json' \
        "${url}" || true)
    if [[ "${code}" != "200" ]]; then
        warn "HTTP ${code} ← ${url}"
        if [[ -f "${out}.tmp" ]]; then
            python3 -m json.tool < "${out}.tmp" >&2 2>/dev/null || cat "${out}.tmp" >&2 || true
            rm -f "${out}.tmp"
        fi
        return 1
    fi
    python3 -m json.tool < "${out}.tmp" > "${out}" 2>/dev/null || mv "${out}.tmp" "${out}"
    rm -f "${out}.tmp"
    return 0
}

unwrap_write() {
    python3 - "$1" "$2" <<'PY'
import json, sys
from pathlib import Path
src, dest = Path(sys.argv[1]), Path(sys.argv[2])
obj = json.loads(src.read_text())
if isinstance(obj, dict) and "data" in obj and "code" in obj:
    obj = obj.get("data")
dest.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
PY
}

# ── 工作空间列表 ────────────────────────────────────────────────────────────
WS_LIST="${OUT_ROOT}/workspaces.json"
if curl_json "${WS_LIST}.raw" "${BASE_URL}/api/v1/system/workspace"; then
    unwrap_write "${WS_LIST}.raw" "${WS_LIST}"
    rm -f "${WS_LIST}.raw"
    info "工作空间列表 → .debug-data/workspaces.json"
else
    warn "无法列出工作空间（需要 admin）。继续用 --oid。"
    rm -f "${WS_LIST}.raw"
fi

if [[ "${LIST_WS}" -eq 1 || -z "${TARGET_OID}" ]]; then
    if [[ -f "${WS_LIST}" ]]; then
        python3 - "${WS_LIST}" <<'PY'
import json, sys
from pathlib import Path
rows = json.loads(Path(sys.argv[1]).read_text()) or []
print("工作空间：")
for ws in rows:
    print(f"  {ws.get('id')}\t{ws.get('name')}")
print()
print("用法: ./scripts/pull-workspace-chats.sh --oid <id>")
PY
    else
        info "未拿到工作空间列表。用法: ./scripts/pull-workspace-chats.sh --oid <id>"
    fi
    [[ "${LIST_WS}" -eq 1 || -z "${TARGET_OID}" ]] && [[ -z "${TARGET_OID}" ]] && exit 0
    [[ "${LIST_WS}" -eq 1 && -z "${TARGET_OID}" ]] && exit 0
fi

OUT_DIR="${OUT_ROOT}/workspace-${TARGET_OID}"
mkdir -p "${OUT_DIR}"

QS="oid=${TARGET_OID}&feedback_only="
if [[ "${FEEDBACK_ONLY}" -eq 1 ]]; then QS="${QS}true"; else QS="${QS}false"; fi
if [[ "${INCLUDE_SQL}" -eq 1 ]]; then QS="${QS}&include_sql=true"; else QS="${QS}&include_sql=false"; fi

info "拉取工作空间 ${TARGET_OID} 对话/反馈…"
EXPORT_URL="${BASE_URL}/api/v1/chat/workspace/export?${QS}"
if ! curl_json "${OUT_DIR}/export.raw.json" "${EXPORT_URL}"; then
    die "导出失败。请确认服务端已部署 GET /api/v1/chat/workspace/export，且账号是 admin 或该空间管理员。"
fi
unwrap_write "${OUT_DIR}/export.raw.json" "${OUT_DIR}/export.json"
rm -f "${OUT_DIR}/export.raw.json"

python3 - "${OUT_DIR}" <<'PY'
import csv, json, sys
from pathlib import Path

out_dir = Path(sys.argv[1])
data = json.loads((out_dir / "export.json").read_text()) or {}
summary = data.get("summary") or {}
oid = data.get("oid")
name = data.get("workspace_name") or ""
chats = data.get("chats") or []

lines = [
    f"# Workspace {oid} — {name}",
    "",
    f"- chats: **{summary.get('chat_count', 0)}**",
    f"- records: **{summary.get('record_count', 0)}**",
    f"- 有帮助: **{summary.get('feedback_up', 0)}**",
    f"- 没帮助: **{summary.get('feedback_down', 0)}**"
    f"  （含描述 {summary.get('feedback_down_with_comment', 0)}）",
    "",
    "## 反馈明细",
]

def trunc(s, n=240):
    s = "" if s is None else str(s)
    return s if len(s) <= n else s[:n] + "…"

voted = []
for chat in chats:
    for rec in chat.get("records") or []:
        if rec.get("feedback"):
            voted.append((chat, rec))

if not voted:
    lines.append("（没有有帮助/没帮助反馈）")
else:
    for chat, rec in voted:
        mark = "👍" if rec.get("feedback") == "up" else "👎"
        lines.append("")
        lines.append(
            f"### {mark} chat `{chat.get('id')}` / record `{rec.get('id')}`"
        )
        who = rec.get("user_name") or rec.get("user_account") or rec.get("create_by")
        lines.append(f"- user: `{who}`  time: `{rec.get('create_time')}`")
        lines.append(f"- question: {trunc(rec.get('question'))}")
        if rec.get("feedback") == "down":
            lines.append(f"- comment: {trunc(rec.get('feedback_comment') or '（无描述）', 800)}")
        if rec.get("sql"):
            lines.append(f"- sql: `{trunc(rec.get('sql'), 400)}`")
        if rec.get("error"):
            lines.append(f"- error: {trunc(rec.get('error'), 400)}")

lines.extend(["", "## 全部对话", ""])
for chat in chats:
    lines.append(
        f"- `{chat.get('id')}` {(chat.get('brief') or '')} "
        f"user=`{chat.get('user_name') or chat.get('user_account')}` "
        f"records={chat.get('record_count')} ds={chat.get('datasource')}"
    )

(out_dir / "FEEDBACK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

csv_path = out_dir / "chats.csv"
with csv_path.open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(
        [
            "chat_id",
            "brief",
            "record_id",
            "user_account",
            "user_name",
            "create_time",
            "question",
            "feedback",
            "feedback_comment",
            "feedback_revision",
            "finish",
            "error",
            "sql",
        ]
    )
    for chat in chats:
        recs = chat.get("records") or [None]
        for rec in recs:
            rec = rec or {}
            writer.writerow(
                [
                    chat.get("id"),
                    chat.get("brief") or "",
                    rec.get("id") or "",
                    rec.get("user_account") or chat.get("user_account") or "",
                    rec.get("user_name") or chat.get("user_name") or "",
                    rec.get("create_time") or chat.get("create_time") or "",
                    rec.get("question") or "",
                    rec.get("feedback") or "",
                    rec.get("feedback_comment") or "",
                    rec.get("feedback_revision") or "",
                    rec.get("finish") if rec else "",
                    rec.get("error") or "",
                    rec.get("sql") or "",
                ]
            )
PY

info "完成 → ${OUT_DIR}/"
echo "  阅读：${OUT_DIR}/FEEDBACK.md"
echo "  全量：${OUT_DIR}/export.json"
echo "  表格：${OUT_DIR}/chats.csv"
