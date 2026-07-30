"""Small shared helpers for configuration tool adapters."""

from __future__ import annotations

from typing import Any

from apps.datasource.models.datasource import CoreDatasource
from common.utils.locale import I18n

_i18n = I18n()


def require_workspace_admin(user: Any) -> None:
    if getattr(user, "isAdmin", False):
        return
    if getattr(user, "weight", 0) == 0:
        raise PermissionError("Only workspace admins can change system configuration")


def require_datasource_scope(
    user: Any,
    datasource: CoreDatasource | None,
    *,
    writable: bool = False,
) -> CoreDatasource:
    if writable:
        require_workspace_admin(user)
    if datasource is None:
        raise ValueError("Datasource not found")
    user_oid = getattr(user, "oid", None)
    if (
        user_oid is not None
        and datasource.oid is not None
        and int(datasource.oid) != int(user_oid)
        and not getattr(user, "isAdmin", False)
    ):
        raise PermissionError(
            f"Datasource {datasource.id} does not belong to current workspace"
        )
    return datasource


def translator_for(user: Any):
    return _i18n(lang=getattr(user, "language", None) or "zh-CN")
