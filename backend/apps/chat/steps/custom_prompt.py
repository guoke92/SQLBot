"""Match licensed custom prompts (domain step)."""

from __future__ import annotations

from typing import Any, Optional

from sqlbot_xpack.custom_prompt.curd.custom_prompt import find_custom_prompts
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum
from sqlbot_xpack.license.license_manage import SQLBotLicenseUtil
from sqlmodel import Session

from apps.chat.curd.chat import end_log, start_log
from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.scope import match_scope


def match_custom_prompts(
    llm_service: Any,
    session: Session,
    custom_prompt_type: CustomPromptTypeEnum,
    oid: Optional[int] = None,
    ds_id: Optional[int] = None,
) -> list[Any]:
    """Fill ``chat_question.custom_prompt`` when license is valid; else no-op."""
    if not SQLBotLicenseUtil.valid():
        return []
    llm_service.current_logs[OperationEnum.FILTER_CUSTOM_PROMPT] = start_log(
        session=session,
        operate=OperationEnum.FILTER_CUSTOM_PROMPT,
        record_id=llm_service.record.id,
        local_operation=True,
    )
    calculate_oid, calculate_ds_id, assistant_id = match_scope(llm_service, oid, ds_id)
    if assistant_id is not None:
        llm_service.chat_question.custom_prompt, prompt_list = find_custom_prompts(
            session,
            custom_prompt_type,
            calculate_oid,
            None,
            assistant_id,
        )
    else:
        llm_service.chat_question.custom_prompt, prompt_list = find_custom_prompts(
            session,
            custom_prompt_type,
            calculate_oid,
            calculate_ds_id,
        )
    llm_service.current_logs[OperationEnum.FILTER_CUSTOM_PROMPT] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.FILTER_CUSTOM_PROMPT],
        full_message=prompt_list,
    )
    return prompt_list
