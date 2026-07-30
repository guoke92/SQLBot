from fastapi import APIRouter

from apps.dictionary.models import (
    DictionaryConfigCreate,
    DictionaryConfigUpdate,
    DictionaryFieldOptionRead,
    DictionaryRefreshResult,
)
from apps.dictionary.service import (
    create_manual_config,
    get_field_option,
    list_field_options,
    refresh_configs,
    update_config,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.audit.models.log_model import OperationModules, OperationType
from common.audit.schemas.logger_decorator import LogConfig, system_log
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["Dictionary"], prefix="/dictionary")


@router.get(
    "/datasource/{ds_id}",
    response_model=list[DictionaryFieldOptionRead],
)
@require_permissions(
    permission=SqlbotPermission(role=["ws_admin"], type="ds", keyExpression="ds_id")
)
async def query_configs(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    table_id: int | None = None,
) -> list[DictionaryFieldOptionRead]:
    return list_field_options(
        session,
        oid=int(user.oid or 1),
        ds_id=ds_id,
        table_id=table_id,
    )


@router.post(
    "/datasource/{ds_id}",
    response_model=DictionaryFieldOptionRead,
)
@system_log(
    LogConfig(
        operation_type=OperationType.CREATE_OR_UPDATE,
        module=OperationModules.DATASOURCE,
        resource_id_expr="ds_id",
    )
)
@require_permissions(
    permission=SqlbotPermission(role=["ws_admin"], type="ds", keyExpression="ds_id")
)
async def add_config(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    data: DictionaryConfigCreate,
) -> DictionaryFieldOptionRead:
    config = create_manual_config(
        session,
        oid=int(user.oid or 1),
        ds_id=ds_id,
        data=data,
    )
    return get_field_option(
        session,
        oid=int(user.oid or 1),
        config_id=int(config.id),
    )


@router.put(
    "/{config_id}",
    response_model=DictionaryFieldOptionRead,
)
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE,
        module=OperationModules.DATASOURCE,
        resource_id_expr="config_id",
    )
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def edit_config(
    session: SessionDep,
    user: CurrentUser,
    config_id: int,
    data: DictionaryConfigUpdate,
) -> DictionaryFieldOptionRead:
    update_config(
        session,
        oid=int(user.oid or 1),
        config_id=config_id,
        data=data,
    )
    return get_field_option(
        session,
        oid=int(user.oid or 1),
        config_id=config_id,
    )


@router.post(
    "/refresh",
    response_model=list[DictionaryRefreshResult],
)
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE,
        module=OperationModules.DATASOURCE,
        resource_id_expr="config_ids",
    )
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
def refresh(
    session: SessionDep,
    user: CurrentUser,
    config_ids: list[int],
) -> list[DictionaryRefreshResult]:
    # A sync route runs in FastAPI's worker pool; the injected Session stays
    # on the same worker thread as the remote extraction call.
    return refresh_configs(
        session,
        oid=int(user.oid or 1),
        config_ids=config_ids,
    )
