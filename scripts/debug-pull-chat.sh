#!/usr/bin/env bash
#
# 从远程服务器拉取对话调试包，尽量完整到可离线复现与定位。
#
# 优先调用 GET /api/v1/chat/{id}/debug_bundle（一次拿齐 record/outcome/intent/log/schema）。
# 若远端尚未部署该接口，则回退到多接口拼装。
#
# 用法：
#   ./scripts/debug-pull-chat.sh <chat_id>
#   ./scripts/debug-pull-chat.sh                 # 拉列表后交互提示；或配合 --all
#   ./scripts/debug-pull-chat.sh --all           # 拉当前用户全部对话（可能很大）
#   ./scripts/debug-pull-chat.sh <chat_id> --full-rows   # 不截断结果行
#
# 环境变量（可覆盖默认）：
#   SQLBOT_DEBUG_BASE_URL   默认 https://et-test.qhhrly.cn
#   SQLBOT_DEBUG_USERNAME   默认 admin
#   SQLBOT_DEBUG_PASSWORD   默认 Lls@123456
#   SQLBOT_DEBUG_MAX_ROWS   默认 50；设为 -1 等同 --full-rows
#
set -euo pipefail

BASE_URL="${SQLBOT_DEBUG_BASE_URL:-https://et-test.qhhrly.cn}"
USERNAME="${SQLBOT_DEBUG_USERNAME:-admin}"
PASSWORD="${SQLBOT_DEBUG_PASSWORD:-Lls@123456}"
MAX_ROWS="${SQLBOT_DEBUG_MAX_ROWS:-50}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${ROOT_DIR}/.debug-data"

PULL_ALL=0
TARGET_CHAT_ID=""

info()  { printf "\033[32m[debug]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[debug] WARN:\033[0m %s\n" "$*" >&2; }
die()   { printf "\033[31m[debug] ERROR:\033[0m %s\n" "$*" >&2; exit 1; }

usage() {
    cat <<'EOF'
用法：
  ./scripts/debug-pull-chat.sh <chat_id>
  ./scripts/debug-pull-chat.sh --all
  ./scripts/debug-pull-chat.sh <chat_id> --full-rows

选项：
  --all          拉取当前用户全部对话
  --full-rows    结果集不截断（默认每步最多 50 行）
  -h, --help     显示帮助

环境变量：SQLBOT_DEBUG_BASE_URL / USERNAME / PASSWORD / MAX_ROWS
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all) PULL_ALL=1 ;;
        --full-rows) MAX_ROWS=-1 ;;
        -h|--help) usage; exit 0 ;;
        -*)
            die "未知参数：$1（见 --help）"
            ;;
        *)
            if [[ -n "${TARGET_CHAT_ID}" ]]; then
                die "多余参数：$1"
            fi
            TARGET_CHAT_ID="$1"
            ;;
    esac
    shift
done

command -v node >/dev/null 2>&1 || die "需要 Node.js"
command -v curl >/dev/null 2>&1 || die "需要 curl"
command -v python3 >/dev/null 2>&1 || die "需要 python3"
mkdir -p "${OUT_DIR}"

# ── 1. xpack 登录拿 token ────────────────────────────────────────────────────
info "登录 ${BASE_URL} …"

LOGIN_JS="$(mktemp /tmp/sqlbot-debug-login.XXXXXX.js)"
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
    # usage: curl_json OUTFILE URL
    local out="$1"
    local url="$2"
    local code
    code=$(curl -sS -o "${out}.tmp" -w '%{http_code}' \
        -H "${AUTH_HEADER}" \
        -H 'Accept: application/json' \
        "${url}" || true)
    if [[ "${code}" != "200" ]]; then
        rm -f "${out}.tmp"
        return 1
    fi
    python3 -m json.tool < "${out}.tmp" > "${out}" 2>/dev/null || mv "${out}.tmp" "${out}"
    rm -f "${out}.tmp"
    return 0
}

# ── 2. 对话列表 ──────────────────────────────────────────────────────────────
info "拉取对话列表…"
if ! curl_json "${OUT_DIR}/chat_list.json" "${BASE_URL}/api/v1/chat/list"; then
    die "拉取对话列表失败"
fi
info "对话列表 → .debug-data/chat_list.json"

# ── 3. 单对话拉取 ────────────────────────────────────────────────────────────
write_analysis_md() {
    local chat_dir="$1"
    python3 - "$chat_dir" <<'PY'
import json, sys
from pathlib import Path

chat_dir = Path(sys.argv[1])
bundle_path = chat_dir / "debug_bundle.json"
lines = []

def trunc(s, n=240):
    s = "" if s is None else str(s)
    return s if len(s) <= n else s[:n] + "…"

def unwrap(obj):
    if isinstance(obj, dict) and "data" in obj and "code" in obj:
        return obj.get("data")
    return obj

if bundle_path.exists():
    bundle = unwrap(json.loads(bundle_path.read_text())) or {}
    chat = bundle.get("chat") or {}
    analysis = bundle.get("analysis") or {}
    ds = bundle.get("datasource") or {}
    lines.append(f"# Chat {bundle.get('chat_id')} — {chat.get('brief') or ''}")
    lines.append("")
    lines.append(f"- exported_at: `{bundle.get('exported_at')}`")
    lines.append(f"- engine: `{chat.get('engine_type')}`  datasource: `{chat.get('datasource')}` ({(ds or {}).get('name')}/{(ds or {}).get('type')})")
    lines.append(f"- records: **{analysis.get('record_count', 0)}**")
    fails = analysis.get("failed_or_degraded") or []
    if fails:
        lines.append(f"- failed/degraded records: **{len(fails)}**")
    lines.append("")
    lines.append("## Records")
    for rec in bundle.get("records") or []:
        rid = rec.get("record_id")
        outcome = rec.get("outcome") or {}
        intent = rec.get("intent_summary") or {}
        lines.append("")
        lines.append(f"### record `{rid}`")
        lines.append(f"- question: {trunc(rec.get('question'))}")
        lines.append(f"- finish: `{rec.get('finish')}`  duration: `{rec.get('duration')}`s")
        if rec.get("error"):
            lines.append(f"- **error**: {trunc(rec.get('error'), 500)}")
        if outcome:
            lines.append(
                f"- outcome: `{outcome.get('status')}` "
                f"({outcome.get('successful_steps')}/{outcome.get('total_steps')}) "
                f"quality={outcome.get('quality_grade')}/{outcome.get('quality_score')}"
            )
            for f in (outcome.get("failures") or [])[:8]:
                lines.append(f"  - failure[{f.get('step_index')}]: `{f.get('kind')}` {trunc(f.get('message'), 180)}")
        if intent:
            lines.append(
                f"- intent: `{intent.get('status')}` "
                f"questions={intent.get('question_count')} "
                f"assumptions={intent.get('assumption_count')} "
                f"issues={intent.get('issue_count')}"
            )
        if rec.get("clarification_parent_id"):
            lines.append(f"- clarification_parent_id: `{rec.get('clarification_parent_id')}`")
        if rec.get("sql"):
            lines.append(f"- sql: `{trunc(rec.get('sql'), 300)}`")
        hot = [
            t for t in (rec.get("timeline") or [])
            if t.get("error") or t.get("operate") in {
                "CLARIFY_INTENT", "GENERATE_QUERY", "EXECUTE_QUERY", "DECIDE_NEXT", "GROUND_ENTITIES"
            }
        ]
        if hot:
            lines.append("- high-signal steps:")
            for t in hot[:20]:
                sig = t.get("signal") or {}
                extra = sig.get("validation_error") or sig.get("error") or sig.get("decision") or sig.get("status") or ""
                mark = " ❌" if t.get("error") else ""
                lines.append(
                    f"  - `{t.get('operate')}`{mark} {t.get('duration')}s "
                    f"node={sig.get('graph_node')} {trunc(extra, 160)}"
                )
    links = analysis.get("clarification_links") or []
    if links:
        lines.append("")
        lines.append("## Clarification chain")
        for link in links:
            lines.append(f"- `{link.get('record_id')}` ← parent `{link.get('parent_id')}`: {trunc(link.get('question'))}")
    lines.append("")
    lines.append("## Files")
    lines.append("- `debug_bundle.json` — 完整调试包（首选）")
    lines.append("- `chat_with_data.json` / `record_*_log.json` — 拆分视图")
    lines.append("- `datasource.json` — 数据源 schema（密钥已脱敏）")
else:
    detail_path = chat_dir / "chat_with_data.json"
    if not detail_path.exists():
        detail_path = chat_dir / "chat_detail.json"
    if detail_path.exists():
        data = unwrap(json.loads(detail_path.read_text())) or {}
        lines.append(f"# Chat {data.get('id')} — {data.get('brief') or ''}")
        lines.append("")
        for r in data.get("records") or []:
            rid = r.get("id")
            lines.append(f"## record {rid}")
            lines.append(f"- question: {trunc(r.get('question'))}")
            if r.get("error"):
                lines.append(f"- error: {trunc(r.get('error'), 400)}")
            payload = r.get("data")
            if isinstance(payload, dict):
                outcome = payload.get("outcome") or {}
                if outcome:
                    lines.append(f"- outcome: `{outcome.get('status')}`")
            intent = r.get("intent_context") or {}
            if isinstance(intent, dict) and intent:
                lines.append(f"- intent.status: `{intent.get('status')}`")
            lines.append("")

(chat_dir / "ANALYSIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(chat_dir / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

pull_chat_fallback() {
    local chat_id="$1"
    local chat_dir="$2"

    info "  [fallback] with_data + per-record log/data…"
    curl_json "${chat_dir}/chat_detail.json" \
        "${BASE_URL}/api/v1/chat/${chat_id}" || warn "  chat_detail 失败"
    curl_json "${chat_dir}/chat_with_data.json" \
        "${BASE_URL}/api/v1/chat/${chat_id}/with_data" || warn "  with_data 失败"

    local source="${chat_dir}/chat_with_data.json"
    [[ -f "${source}" ]] || source="${chat_dir}/chat_detail.json"
    [[ -f "${source}" ]] || return 1

    local ds_id
    ds_id=$(python3 -c "
import json
d=json.load(open('${source}')).get('data') or {}
print(d.get('datasource') or '')
" 2>/dev/null || true)

    if [[ -n "${ds_id}" ]]; then
        curl -sS -X POST "${BASE_URL}/api/v1/datasource/get/${ds_id}" \
            -H "${AUTH_HEADER}" -H 'Accept: application/json' \
            | python3 -m json.tool > "${chat_dir}/datasource.json" 2>/dev/null \
            || warn "  datasource get 失败"
        curl -sS -X POST "${BASE_URL}/api/v1/datasource/tableList/${ds_id}" \
            -H "${AUTH_HEADER}" -H 'Accept: application/json' \
            | python3 -m json.tool > "${chat_dir}/datasource_tables.json" 2>/dev/null \
            || true
        curl -sS -X POST "${BASE_URL}/api/v1/table_relation/get/${ds_id}" \
            -H "${AUTH_HEADER}" -H 'Accept: application/json' \
            | python3 -m json.tool > "${chat_dir}/datasource_relations.json" 2>/dev/null \
            || true
    fi

    local record_ids
    record_ids=$(python3 -c "
import json
d=json.load(open('${source}')).get('data') or {}
for r in d.get('records') or []:
    rid=r.get('id')
    if rid: print(rid)
" 2>/dev/null || true)

    for rid in ${record_ids}; do
        info "  拉取 record ${rid} log/data/usage…"
        curl_json "${chat_dir}/record_${rid}_log.json" \
            "${BASE_URL}/api/v1/chat/record/${rid}/log" || \
            echo '{"error":"log pull failed"}' > "${chat_dir}/record_${rid}_log.json"
        curl_json "${chat_dir}/record_${rid}_data.json" \
            "${BASE_URL}/api/v1/chat/record/${rid}/data" || true
        curl_json "${chat_dir}/record_${rid}_usage.json" \
            "${BASE_URL}/api/v1/chat/record/${rid}/usage" || true
        # predict_data if present on record
        python3 -c "
import json,sys
d=json.load(open('${source}')).get('data') or {}
for r in d.get('records') or []:
    if str(r.get('id'))=='${rid}' and r.get('predict_record_id'):
        sys.exit(0)
sys.exit(1)
" 2>/dev/null && curl_json "${chat_dir}/record_${rid}_predict_data.json" \
            "${BASE_URL}/api/v1/chat/record/${rid}/predict_data" || true
    done
}

pull_chat() {
    local chat_id="$1"
    local chat_dir="${OUT_DIR}/${chat_id}"
    mkdir -p "${chat_dir}"

    info "拉取对话 ${chat_id}…"
    local bundle_url="${BASE_URL}/api/v1/chat/${chat_id}/debug_bundle?max_rows=${MAX_ROWS}&include_raw_logs=true"
    if curl_json "${chat_dir}/debug_bundle.json" "${bundle_url}"; then
        info "  debug_bundle OK"
        # Also split convenient views for quick open
        python3 - "$chat_dir" <<'PY'
import json
from pathlib import Path
chat_dir = Path(__import__("sys").argv[1])

def unwrap(obj):
    if isinstance(obj, dict) and "data" in obj and "code" in obj:
        return obj.get("data")
    return obj

raw = json.loads((chat_dir / "debug_bundle.json").read_text())
bundle = unwrap(raw) or {}
# Rewrite file as unwrapped bundle for easier offline use
(chat_dir / "debug_bundle.json").write_text(
    json.dumps(bundle, ensure_ascii=False, indent=2, default=str),
    encoding="utf-8",
)
chat = bundle.get("chat") or {}
records_view = []
for rec in bundle.get("records") or []:
    records_view.append({
        "id": rec.get("record_id"),
        "chat_id": rec.get("chat_id"),
        "question": rec.get("question"),
        "error": rec.get("error"),
        "finish": rec.get("finish"),
        "sql": rec.get("sql"),
        "data": rec.get("answer_payload"),
        "intent_context": rec.get("intent_context"),
        "clarification_parent_id": rec.get("clarification_parent_id"),
        "outcome": rec.get("outcome"),
        "re_exec": rec.get("re_exec"),
        "duration": rec.get("duration"),
        "ai_modal_id": rec.get("ai_modal_id"),
    })
    rid = rec.get("record_id")
    (chat_dir / f"record_{rid}_log.json").write_text(
        json.dumps({"code": 0, "data": rec.get("log"), "msg": None}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (chat_dir / f"record_{rid}_timeline.json").write_text(
        json.dumps(rec.get("timeline") or [], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    if rec.get("answer_payload") is not None:
        (chat_dir / f"record_{rid}_data.json").write_text(
            json.dumps({"code": 0, "data": rec.get("answer_payload"), "msg": None}, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
(chat_dir / "chat_with_data.json").write_text(
    json.dumps({"code": 0, "data": {**chat, "records": records_view}, "msg": None}, ensure_ascii=False, indent=2, default=str),
    encoding="utf-8",
)
if bundle.get("datasource") is not None:
    (chat_dir / "datasource.json").write_text(
        json.dumps(bundle.get("datasource"), ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
if bundle.get("ai_models") is not None:
    (chat_dir / "ai_models.json").write_text(
        json.dumps(bundle.get("ai_models"), ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
(chat_dir / "analysis_index.json").write_text(
    json.dumps(bundle.get("analysis") or {}, ensure_ascii=False, indent=2, default=str),
    encoding="utf-8",
)
PY
    else
        warn "  debug_bundle 不可用，回退多接口拼装（请确认服务已部署新接口）"
        pull_chat_fallback "${chat_id}" "${chat_dir}" || {
            warn "  对话 ${chat_id} 拉取失败，跳过"
            return
        }
    fi

    write_analysis_md "${chat_dir}"
    info "  完成 → .debug-data/${chat_id}/（ANALYSIS.md + debug_bundle.json）"
}

# ── main ─────────────────────────────────────────────────────────────────────
if [[ "${PULL_ALL}" -eq 1 ]]; then
    CHAT_IDS=$(python3 -c "
import json
data=json.load(open('${OUT_DIR}/chat_list.json')).get('data') or []
for c in data:
    cid=c.get('id')
    if cid: print(cid)
")
    [[ -n "${CHAT_IDS}" ]] || { info "无对话记录"; exit 0; }
    for CID in ${CHAT_IDS}; do
        pull_chat "${CID}"
    done
elif [[ -n "${TARGET_CHAT_ID}" ]]; then
    pull_chat "${TARGET_CHAT_ID}"
else
    info "未指定 chat_id。最近对话："
    python3 -c "
import json
data=json.load(open('${OUT_DIR}/chat_list.json')).get('data') or []
for c in data[:15]:
    print(f\"  {c.get('id')}\t{(c.get('brief') or '')[:40]}\t{c.get('create_time')}\")
print()
print('用法: ./scripts/debug-pull-chat.sh <chat_id>')
"
    exit 0
fi

echo
info "全部完成。数据在 .debug-data/"
echo "  优先阅读：.debug-data/<chatId>/ANALYSIS.md"
echo "  完整包：  .debug-data/<chatId>/debug_bundle.json"
echo "  过程日志：.debug-data/<chatId>/record_*_log.json / *_timeline.json"
