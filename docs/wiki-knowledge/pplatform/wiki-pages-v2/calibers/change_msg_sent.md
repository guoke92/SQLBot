---
type: caliber
title: 变更消息已发送
page_key: change_msg_sent
domain: 客户中心
status: draft
aliases:
  - isMsgNotify
  - 变更消息幂等
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:isMsgNotify
contract_version: "0.1"
belong: calibers
---

变更消息已发送口径用于审核回调的幂等判断：同一变更记录在当前审核状态下若消息已发送（msg_send=Y）则不再重复通知。关联 [[cust_change_record]] 与状态机 [[cust_change_check]]。

```ground:caliber
name: 变更消息已发送
predicate: "cust_change_record.status = '<当前审核状态>' AND cust_change_record.msg_send = 'Y'"
scope: isMsgNotify 幂等判断
evidence: code_path:CustStatusCommitProcessor.java:isMsgNotify
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。