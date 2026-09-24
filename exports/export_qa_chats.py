#!/usr/bin/env python3
"""Download qa-admin Excel export via /dev/qa-admin/feedback.xlsx.

Uses the same server-side builder as the 智能问数管理「导出反馈」button
(apps.dev.qa_export.build_qa_chats_workbook).

Auth: set SQLBOT_TOKEN (raw JWT or ``Bearer …``) and optionally SQLBOT_BASE / SQLBOT_OID.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = os.environ.get("SQLBOT_BASE", "https://et-test.qhhrly.cn/api/v1/dev/qa-admin")
OID = os.environ.get("SQLBOT_OID", "7504090896279801856")
OUT = Path(__file__).resolve().parent / "qa-admin-chats-export.xlsx"


def _token() -> str:
    raw = (os.environ.get("SQLBOT_TOKEN") or "").strip()
    if not raw:
        print(
            "Set SQLBOT_TOKEN to a qa-admin JWT (with or without 'Bearer ' prefix).",
            file=sys.stderr,
        )
        sys.exit(1)
    return raw if raw.lower().startswith("bearer ") else f"Bearer {raw}"


def main() -> None:
    query = urllib.parse.urlencode({"oid": OID, "chat_type": "chat"})
    req = urllib.request.Request(
        f"{BASE}/feedback.xlsx?{query}",
        headers={
            "accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "accept-language": "zh-CN",
            "x-sqlbot-token": _token(),
            "user-agent": "SQLBot-export-script/1.2",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = resp.read()
    OUT.write_bytes(body)
    print(
        json.dumps(
            {
                "out": str(OUT),
                "bytes": len(body),
                "endpoint": f"{BASE}/feedback.xlsx",
                "note": "Excel built by apps.dev.qa_export (same as qa-admin UI)",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
