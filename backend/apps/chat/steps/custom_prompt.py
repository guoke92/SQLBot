"""Match licensed custom prompts (domain step)."""

from __future__ import annotations

from typing import Any, Optional

from sqlbot_xpack.custom_prompt.curd.custom_prompt import find_custom_prompts
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum
from sqlbot_xpack.license.license_manage import SQLBotLicenseUtil
from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.scope import match_scope
from apps.chat.steps.observability import log_span


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
    with log_span(
        operate=OperationEnum.FILTER_CUSTOM_PROMPT,
        record_id=llm_service.record.id,
        local_operation=True,
        graph_node="retrieve_context",
        title_key="chat.log.FILTER_CUSTOM_PROMPT",
    ) as span:
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
        span.set_detail({"prompt_count": len(prompt_list), "prompts": prompt_list})
        span.set_summary("chat.audit.prompts_ready", count=len(prompt_list))
    return prompt_list
