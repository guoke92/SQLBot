---
type: process
title: "变更记录审核状态机"
page_key: "processes/change_record_check_machine"
domain: "customer-onboarding"
status: draft
aliases:
  - "变更审核流转"
  - "cust_change_record.status 状态机"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:changeMessage(recordDO.setStatus + setMsgSend=Y)"
  - "code_path:CustStatusCommitProcessor.java:changeMessage"
  - "code_path:CustStatusCommitProcessor.java:changeMessage(checkAdvice.contains(\"退回\") && SELF_ALTER)"
contract_version: "0.1"
---

变更记录审核状态机描述 `cust_change_record.status` 的流转。与工作流审核状态机不同，本状态机在退回场景会写入 `returnCust-yyyy-MM-dd HH:mm` 这类按分钟动态生成的非枚举值，因此基于枚举的状态口径不能完整覆盖该分支，需以 [[tables/cust_change_record]] 的实际值为准。

## 需求背景

需求文档主张：企业变更需经审核，审核通过后变更生效，驳回则记录状态为已驳回并通知。该主张与代码一致：`CustStatusCommitProcessor.java:changeMessage` 按 `CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 更新 `cust_change_record.status`，并在同处写入 `msg_send=Y` 并发起短信/站内信通知。

通知的幂等与弱失败策略见 [[rules/message_send_weak_failure_dedup]] 与 [[calibers/callback_msg_idempotent]]；回查等待见 [[calibers/change_record_polling]]。

## 版本演进

- 退回分支从「统一枚举」演化为「按分钟动态值」，动态值仅在 `rtfComment` 含「退回」且变更方式为企业自行提交（`SELF_ALTER`）时写入，见本页 transitions。
- 本状态机的变更消息逻辑所在处理器已 `@Deprecated`，新链路替代，见 [[rules/legacy_status_processor_deprecated]]。

```ground:process
name: 变更记录审核状态机
field: cust_change_record.status
states:
  - value: "CUST_CHECK_PASS"
    label: "审核通过"
    source: "code_enum"
  - value: "CUST_CHECK_REJECT"
    label: "审核拒绝"
    source: "code_enum"
  - value: "CUST_CHECK_BACKTOCUSTOM"
    label: "待客户确认"
    source: "code_enum"
  - value: "returnCust-yyyy-MM-dd HH:mm"
    label: "退回（自行变更场景，按分钟动态生成）"
    source: "code_enum"
transitions:
  - from: "CUST_CHECK_BACKTOCUSTOM"
    event: "运营中台变更审核通过(CUST_CHECK_PASS)"
    to: "CUST_CHECK_PASS"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage(recordDO.setStatus + setMsgSend=Y)"
  - from: "CUST_CHECK_BACKTOCUSTOM"
    event: "运营中台变更审核拒绝(CUST_CHECK_REJECT)"
    to: "CUST_CHECK_REJECT"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage"
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台退回待客户确认(CUST_CHECK_BACKTOCUSTOM)"
    to: "CUST_CHECK_BACKTOCUSTOM"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage"
  - from: "CUST_CHECK_CHECKING"
    event: "rtfComment 含『退回』且变更为企业自行提交(SELF_ALTER)"
    to: "returnCust-yyyy-MM-dd HH:mm"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage(checkAdvice.contains(\"退回\") && SELF_ALTER)"
reqdoc_anchors:
  - claim: "企业变更需经审核，审核通过后变更生效，驳回则记录状态为已驳回并通知"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage + reqdoc:company-change-audit-notify"
```

相关：[[tables/cust_change_record]]、[[calibers/callback_msg_idempotent]]、[[rules/message_send_weak_failure_dedup]]。