from typing import Any

from fastapi import APIRouter, Path

from apps.datasource.relation_service import get_relation_graph, save_relation_graph
from apps.swagger.i18n import PLACEHOLDER_PREFIX
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.audit.models.log_model import OperationType, OperationModules
from common.audit.schemas.logger_decorator import LogConfig, system_log
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["Table Relation"], prefix="/table_relation")


@router.post("/save/{ds_id}", response_model=None, summary=f"{PLACEHOLDER_PREFIX}tr_save")
@require_permissions(
    permission=SqlbotPermission(
        role=["ws_admin"],
        keyExpression="ds_id",
        type="ds",
    )
)
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE_TABLE_RELATION,
        module=OperationModules.DATASOURCE,
        resource_id_expr="ds_id",
    )
)
async def save_relation(
    session: SessionDep,
    relation: list[dict[str, Any]],
    current_user: CurrentUser,
    ds_id: int = Path(..., description=f"{PLACEHOLDER_PREFIX}ds_id"),
):
    save_relation_graph(
        session,
        oid=int(current_user.oid or 1),
        ds_id=ds_id,
        graph=relation,
    )
    return True


@router.post(
    "/get/{ds_id}",
    response_model=list,
    summary=f"{PLACEHOLDER_PREFIX}tr_get",
)
@require_permissions(
    permission=SqlbotPermission(
        role=["ws_admin"],
        keyExpression="ds_id",
        type="ds",
    )
)
async def get_relation(
    session: SessionDep,
    current_user: CurrentUser,
    ds_id: int = Path(..., description=f"{PLACEHOLDER_PREFIX}ds_id"),
):
    return get_relation_graph(
        session,
        oid=int(current_user.oid or 1),
        ds_id=ds_id,
    )
