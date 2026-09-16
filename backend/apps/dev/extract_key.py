"""Single rotatable extract key: hashed at rest, plaintext returned once."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.dev.models import ConversationExtractKey

EXTRACT_HEADER = "X-SQLBOT-EXTRACT-KEY"
_PREFIX_LEN = 8


def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_key_row(session: Session) -> ConversationExtractKey | None:
    return session.exec(select(ConversationExtractKey)).first()


def verify_extract_key(session: Session, raw: str | None) -> bool:
    if not raw or not str(raw).strip():
        return False
    row = get_key_row(session)
    if row is None:
        return False
    return hmac.compare_digest(row.key_hash, hash_key(str(raw).strip()))


def public_key_info(row: ConversationExtractKey | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "key_prefix": row.key_prefix,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "created_by": row.created_by,
    }


def rotate_key(session: Session, created_by: int) -> str:
    plaintext = secrets.token_urlsafe(32)
    prefix = plaintext[:_PREFIX_LEN]
    digest = hash_key(plaintext)
    existing = list(session.exec(select(ConversationExtractKey)).all())
    for row in existing:
        session.delete(row)
    session.add(
        ConversationExtractKey(
            key_prefix=prefix,
            key_hash=digest,
            created_at=datetime.now(),
            created_by=int(created_by),
        )
    )
    session.commit()
    return plaintext


def revoke_key(session: Session) -> None:
    existing = list(session.exec(select(ConversationExtractKey)).all())
    for row in existing:
        session.delete(row)
    session.commit()
