---
type: caliber
title: "回调消息幂等去重"
page_key: callback_msg_idempotent
domain: "customer-onboarding"
status: draft
aliases:
  - "通知去重口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:isMsgNotify"
contract_version: "0.1"
belong: calibers
---

运营中台回调可能重入，为避免同一审核结论重复发短信/站内信，发送前按「状态相同且已发送」判定跳过。该口径依赖 [[tables/cust_change_record]] 的 `msg_send` 标记，配合消息发送的弱失败策略见 [[rules/message_send_weak_failure_dedup]]。

## 需求背景

需求文档要求驳回等结果需通知企业；通知需保证「不重不漏」，重入场景以本口径去重。

## 版本演进

- 去重键由单纯状态比较演进为「状态 + 发送标记」双条件，避免同状态二次流转被误判。

```ground:caliber
name: "回调消息幂等去重"
predicate: "cust_change_record.status = 本次审核状态 AND cust_change_record.msg_send = 'Y'"
scope: "isMsgNotify 判定消息无需重复发送"
evidence: "code_path:CustStatusCommitProcessor.java:isMsgNotify"
```

相关：[[tables/cust_change_record]]、[[rules/message_send_weak_failure_dedup]]、[[processes/change_record_check_machine]]。