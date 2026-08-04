#!/usr/bin/env bash
# 兼容旧部署流程：安装逻辑已经合并到 init.sh。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
printf "\033[33m[sqlbot] install.sh 已合并到 init.sh，转交 init.sh 执行。\033[0m\n"
exec "${SCRIPT_DIR}/init.sh" "$@"
