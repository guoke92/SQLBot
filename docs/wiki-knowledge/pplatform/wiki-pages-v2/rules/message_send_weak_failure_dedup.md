---
type: rule
title: "消息发送弱失败与去重"
page_key: message_send_weak_failure_dedup
domain: "customer-onboarding"
status: draft
aliases:
  - "消息弱失败"
  - "通知去重规则"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustMessageSendService.java:sendSms,isSend"
  - "code_path:CustStatusCommitProcessor.java:isMsgNotify"
contract_version: "0.1"
belong: rules
---

所有短信、站内信、消息发送接口均以 try-catch 包裹并仅记日志、不向上抛出；变更回调在发送前先查最近一次通知的发送标记，已发送则跳过。结果是：消息通道可用性不影响状态落库，且回调可安全重入。去重口径见 [[calibers/callback_msg_idempotent]]，标记字段见 [[tables/cust_change_record]]。

## 需求背景

需求文档要求审核结果通知企业；同时状态落库不能因为通知失败而回滚，因此把通知定义为「尽力而为 + 幂等」。

## 版本演进

- 由「发送失败即影响主流程」演进为弱失败；去重标记 `msg_send` 随之成为回调可重入的前提。

```ground:rule
name: "消息发送弱失败与去重"
content: "CustMessageSendService 所有 sendSms/sendNotice/sendMessage 均 try-catch 记录日志不抛出；变更回调发送前用 isSend()/isMsgNotify() 查询最近一次通知，已发送则跳过。"
impact: "消息失败不影响主流程，回调可重入"
field_targets:
  - "cust_change_record.msg_send"
evidence: "code_path:CustMessageSendService.java:sendSms,isSend;CustStatusCommitProcessor.java:isMsgNotify"
```

相关：[[calibers/callback_msg_idempotent]]、[[processes/change_record_check_machine]]、[[tables/cust_change_record]]。