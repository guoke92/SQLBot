"""SQL / chart result parse + persist helpers (domain atoms)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import orjson
from sqlmodel import Session

from apps.chat.curd.chat import (
    save_chart,
    save_sql,
    save_sql_exec_data,
    trigger_log_error,
)
from apps.chat.models.chat_model import OperationEnum
from common.error import SingleMessageError
from common.utils.data_format import DataFormat
from common.utils.utils import extract_nested_json, prepare_for_orjson


def check_sql(
    llm_service: Any, session: Session, res: str, operate: OperationEnum
) -> tuple[str, Optional[list]]:
    """Parse SQL JSON blob from model text; raise SingleMessageError on failure."""
    json_str = extract_nested_json(res)
    log = llm_service.current_logs[operate]
    if json_str is None:
        trigger_log_error(session, log)
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "SQL answer is not a valid json object",
                    "traceback": "SQL answer is not a valid json object:\n" + res,
                }
            ).decode()
        )
    try:
        data = orjson.loads(json_str)
        if data["success"]:
            sql = data["sql"]
        else:
            raise SingleMessageError(data["message"])
    except SingleMessageError as e:
        trigger_log_error(session, log)
        raise e
    except Exception:
        trigger_log_error(session, log)
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "Cannot parse sql from answer",
                    "traceback": "Cannot parse sql from answer:\n" + res,
                }
            ).decode()
        )
    if sql.strip() == "":
        trigger_log_error(session, log)
        raise SingleMessageError("SQL query is empty")
    return sql, data.get("tables")


def check_save_sql(
    llm_service: Any, session: Session, res: str, operate: OperationEnum
) -> str:
    sql, *_ = check_sql(llm_service, session, res=res, operate=operate)
    save_sql(session=session, sql=sql, record_id=llm_service.record.id)
    llm_service.chat_question.sql = sql
    return sql


def check_save_chart(
    llm_service: Any,
    session: Session,
    res: str,
    fields: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    json_str = extract_nested_json(res)
    if json_str is None:
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "Cannot parse chart config from answer",
                    "traceback": "Cannot parse chart config from answer:\n" + res,
                }
            ).decode()
        )
    chart: Dict[str, Any] = {}
    message = ""
    error = False
    try:
        data = orjson.loads(json_str)
        if data["type"] and data["type"] != "error":
            chart = data
            DataFormat.align_chart_bindings(chart, fields)
        elif data["type"] == "error":
            message = data["reason"]
            error = True
        else:
            raise Exception("Chart is empty")
    except Exception:
        error = True
        message = orjson.dumps(
            {
                "message": "Cannot parse chart config from answer",
                "traceback": "Cannot parse chart config from answer:\n" + res,
            }
        ).decode()
    if error:
        raise SingleMessageError(message)
    save_chart(
        session=session, chart=orjson.dumps(chart).decode(), record_id=llm_service.record.id
    )
    return chart


def save_sql_data(
    llm_service: Any, session: Session, data_obj: Dict[str, Any]
) -> Any:
    try:
        data_result = data_obj.get("data")
        limit = 1000
        if data_result:
            data_result = prepare_for_orjson(data_result)
            if data_result and len(data_result) > limit and llm_service.enable_sql_row_limit:
                data_obj["data"] = data_result[:limit]
                data_obj["limit"] = limit
            else:
                data_obj["data"] = data_result
            data_obj["datasource"] = llm_service.ds.id
        return save_sql_exec_data(
            session=session,
            record_id=llm_service.record.id,
            data=orjson.dumps(data_obj).decode(),
        )
    except Exception as e:
        raise e
