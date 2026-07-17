#!/usr/bin/env bash
set -euo pipefail

# ── resolve paths ──────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "${SCRIPT_DIR}/backend" && -d "${SCRIPT_DIR}/frontend" ]]; then
    ROOT_DIR="${SCRIPT_DIR}"
elif [[ -d "${SCRIPT_DIR}/../backend" && -d "${SCRIPT_DIR}/../frontend" ]]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
elif [[ -f "${SCRIPT_DIR}/../main.py" ]]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
else
    ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
ENV_FILE="${ROOT_DIR}/.env"
DATA_DIR="${ROOT_DIR}/data"
RUN_DIR="${DATA_DIR}/run"
LOG_DIR="${DATA_DIR}/logs"
BACKEND_PID_FILE="${RUN_DIR}/backend.pid"
FRONTEND_PID_FILE="${RUN_DIR}/frontend.pid"
BACKEND_LOG="${LOG_DIR}/backend-dev.log"
FRONTEND_LOG="${LOG_DIR}/frontend-dev.log"
UVICORN_BIN="${BACKEND_DIR}/venv/bin/uvicorn"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
ACTION="${1:-}"
TARGET="${2:-all}"

# ── helpers ─────────────────────────────────────────────────────────────────
info()  { printf "\033[32m[sqlbot]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[sqlbot] WARN:\033[0m %s\n" "$*" >&2; }
err()   { printf "\033[31m[sqlbot] ERROR:\033[0m %s\n" "$*" >&2; }

ensure_dirs() {
    mkdir -p "${RUN_DIR}" "${LOG_DIR}" \
        "${DATA_DIR}/file" "${DATA_DIR}/images" \
        "${DATA_DIR}/excel" "${DATA_DIR}/models" \
        "${DATA_DIR}/scripts"
}

is_pid_running() { local pid="${1:-}"; [[ -n "${pid}" && "${pid}" =~ ^[0-9]+$ ]] && kill -0 "${pid}" 2>/dev/null; }

pid_from_file() { local f="$1"; [[ -f "$f" ]] && tr -d "[:space:]" <"$f" || true; }

port_pid() { local port="$1"; lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null | awk 'NR==2{print $2}' || true; }

graceful_kill() {
    local pid="$1" label="${2:-process}"
    if ! is_pid_running "$pid"; then return 0; fi
    info "Stopping ${label} (pid=${pid})…"
    kill "$pid" 2>/dev/null || true
    local waited=0
    while is_pid_running "$pid" && [[ $waited -lt 15 ]]; do sleep 1; ((waited++)); done
    if is_pid_running "$pid"; then
        warn "${label} did not stop — force-killing"
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
}

force_kill_port() {
    local port="$1" label="${2:-}"
    local pid; pid="$(port_pid "$port")"
    if [[ -n "$pid" ]]; then
        graceful_kill "$pid" "${label:-port $port}"
    fi
}

env_set() {
    # Set or update a KEY=value in the .env file (no value = delete line).
    local key="$1" val="${2:-}"
    if grep -qE "^[[:space:]]*${key}[[:space:]]*=" "${ENV_FILE}" 2>/dev/null; then
        if [[ -n "$val" ]]; then
            sed -i '' "s|^[[:space:]]*${key}[[:space:]]*=.*|${key}=${val}|" "${ENV_FILE}"
        else
            sed -i '' "/^[[:space:]]*${key}[[:space:]]*=/d" "${ENV_FILE}"
        fi
    else
        [[ -n "$val" ]] && echo "${key}=${val}" >>"${ENV_FILE}"
    fi
}

env_get() {
    local key="$1"
    grep -E "^[[:space:]]*${key}[[:space:]]*=" "${ENV_FILE}" 2>/dev/null | head -1 | sed 's/^[^=]*=[[:space:]]*//' || true
}

ollama_probe() {
    # Returns 0 if Ollama answers /api/tags
    curl -sf --max-time 3 http://localhost:11434/api/tags >/dev/null 2>&1
}

# ── setup-env ───────────────────────────────────────────────────────────────
setup_env() {
    info "Configuring .env for local development…"
    ensure_dirs

    [[ -f "${ENV_FILE}" ]] || touch "${ENV_FILE}"

    # ---- embedding (Ollama) -------------------------------------------------
    env_set EMBEDDING_PROVIDER      ollama
    env_set EMBEDDING_API_BASE      "http://localhost:11434/v1"
    env_set EMBEDDING_API_KEY       ollama
    env_set DEFAULT_EMBEDDING_MODEL jina-embed
    env_set EMBEDDING_ENABLED       True
    env_set TABLE_EMBEDDING_ENABLED True
    env_set EMBEDDING_DEFAULT_SIMILARITY 0.4

    info "Embedding config written → Ollama jina-embed (provider=ollama)"
    info ".env = ${ENV_FILE}"

    if ollama_probe; then
        info "Ollama is reachable at http://localhost:11434"
    else
        warn "Ollama not reachable at http://localhost:11434 — start it first"
    fi
}

# ── start / stop backend ────────────────────────────────────────────────────
start_backend() {
    local pid; pid="$(pid_from_file "${BACKEND_PID_FILE}")"
    if is_pid_running "$pid"; then
        warn "Backend already running (pid=${pid})"
        return 0
    fi
    # kill stale port occupant
    force_kill_port "${BACKEND_PORT}" "stale-backend"

    info "Starting backend (uvicorn on :${BACKEND_PORT})…"
    ensure_dirs
    (
        cd "${BACKEND_DIR}"
        "${UVICORN_BIN}" main:app --host 0.0.0.0 --port "${BACKEND_PORT}" --reload \
            >>"${BACKEND_LOG}" 2>&1 &
        echo $! >"${BACKEND_PID_FILE}"
    )
    sleep 2
    if pid="$(pid_from_file "${BACKEND_PID_FILE}")" && is_pid_running "$pid"; then
        info "Backend started (pid=${pid})  http://localhost:${BACKEND_PORT}/docs"
    else
        err "Backend failed to start — tail ${BACKEND_LOG}"
        return 1
    fi
}

stop_backend() {
    local pid; pid="$(pid_from_file "${BACKEND_PID_FILE}")"
    if is_pid_running "$pid"; then
        graceful_kill "$pid" "backend"
    fi
    rm -f "${BACKEND_PID_FILE}"
    force_kill_port "${BACKEND_PORT}" "backend-port"
    info "Backend stopped"
}

# ── start / stop frontend ───────────────────────────────────────────────────
start_frontend() {
    local pid; pid="$(pid_from_file "${FRONTEND_PID_FILE}")"
    if is_pid_running "$pid"; then
        warn "Frontend already running (pid=${pid})"
        return 0
    fi
    force_kill_port "${FRONTEND_PORT}" "stale-frontend"

    info "Starting frontend (vite on :${FRONTEND_PORT})…"
    ensure_dirs
    (
        cd "${FRONTEND_DIR}"
        npx vite --host 0.0.0.0 --port "${FRONTEND_PORT}" \
            >>"${FRONTEND_LOG}" 2>&1 &
        echo $! >"${FRONTEND_PID_FILE}"
    )
    sleep 2
    if pid="$(pid_from_file "${FRONTEND_PID_FILE}")" && is_pid_running "$pid"; then
        info "Frontend started (pid=${pid})  http://localhost:${FRONTEND_PORT}"
    else
        err "Frontend failed to start — tail ${FRONTEND_LOG}"
        return 1
    fi
}

stop_frontend() {
    local pid; pid="$(pid_from_file "${FRONTEND_PID_FILE}")"
    if is_pid_running "$pid"; then
        graceful_kill "$pid" "frontend"
    fi
    rm -f "${FRONTEND_PID_FILE}"
    force_kill_port "${FRONTEND_PORT}" "frontend-port"
    info "Frontend stopped"
}

# ── status ──────────────────────────────────────────────────────────────────
status_all() {
    echo "=============================="
    echo " SQLBot Dev Status"
    echo "=============================="

    # Backend
    local bpid; bpid="$(pid_from_file "${BACKEND_PID_FILE}")"
    if is_pid_running "$bpid"; then
        echo "  Backend  : RUNNING  pid=${bpid}  http://localhost:${BACKEND_PORT}/docs"
    else
        echo "  Backend  : STOPPED"
    fi

    # Frontend
    local fpid; fpid="$(pid_from_file "${FRONTEND_PID_FILE}")"
    if is_pid_running "$fpid"; then
        echo "  Frontend : RUNNING  pid=${fpid}  http://localhost:${FRONTEND_PORT}"
    else
        echo "  Frontend : STOPPED"
    fi

    # Ollama
    if ollama_probe; then
        echo "  Ollama   : REACHABLE  http://localhost:11434"
    else
        echo "  Ollama   : NOT REACHABLE"
    fi

    echo "------------------------------"
    echo "  Logs: ${BACKEND_LOG}"
    echo "        ${FRONTEND_LOG}"
    echo "=============================="
}

# ── dispatch ────────────────────────────────────────────────────────────────
usage() {
    echo "Usage: sqlbot-dev.sh <command> [target]"
    echo ""
    echo "Commands:"
    echo "  setup-env         Write Ollama embedding + local paths into .env"
    echo "  start [all|backend|frontend]"
    echo "  stop  [all|backend|frontend]"
    echo "  restart [all|backend|frontend]"
    echo "  status"
    exit 1
}

dispatch() {
    case "${ACTION}" in
        setup-env|setup_env)
            setup_env ;;
        start)
            case "${TARGET}" in
                all|"")
                    start_backend
                    start_frontend
                    status_all ;;
                backend) start_backend ;;
                frontend) start_frontend ;;
                *) usage ;;
            esac ;;
        stop)
            case "${TARGET}" in
                all|"")
                    stop_backend
                    stop_frontend ;;
                backend) stop_backend ;;
                frontend) stop_frontend ;;
                *) usage ;;
            esac ;;
        restart)
            case "${TARGET}" in
                all|"")
                    stop_backend; stop_frontend
                    start_backend; start_frontend
                    status_all ;;
                backend)
                    stop_backend; start_backend ;;
                frontend)
                    stop_frontend; start_frontend ;;
                *) usage ;;
            esac ;;
        status)
            status_all ;;
        *)
            usage ;;
    esac
}

dispatch
