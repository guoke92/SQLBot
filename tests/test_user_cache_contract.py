from __future__ import annotations

import sys
import asyncio
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.system.crud import user as user_crud  # noqa: E402
from apps.system.schemas.system_schema import UserInfoDTO  # noqa: E402


def test_cached_user_mapping_is_rehydrated_to_dto(monkeypatch) -> None:
    async def cached(**_kwargs):
        return {
            "id": 1,
            "account": "admin",
            "name": "Administrator",
            "email": "admin@example.invalid",
            "oid": 1,
            "language": "zh-CN",
            "isAdmin": True,
        }

    monkeypatch.setattr(user_crud, "_get_user_info_cached", cached)
    result = asyncio.run(user_crud.get_user_info(session=object(), user_id=1))

    assert isinstance(result, UserInfoDTO)
    assert result.language == "zh-CN"
