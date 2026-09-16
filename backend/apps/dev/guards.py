"""Platform-admin gate for /dev/qa-admin and extract-key. Non-admins get 404."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException

from apps.system.schemas.system_schema import UserInfoDTO
from common.core.deps import CurrentUser


def require_dev_admin(current_user: CurrentUser) -> UserInfoDTO:
    if not bool(getattr(current_user, "isAdmin", False)):
        raise HTTPException(status_code=404, detail="Not found")
    return current_user


DevAdmin = Annotated[UserInfoDTO, Depends(require_dev_admin)]
