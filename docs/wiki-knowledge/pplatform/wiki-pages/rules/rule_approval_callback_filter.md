---
type: rule
title: 运营中台审批回调过滤规则
page_key: rule_approval_callback_filter
belong: rules
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustSyncEventProvider.onEvent", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.check_status]
coverage_note: 企业
scope:
  databases: [lowcode_pplatform]
---

该规则在运营中台审批回调进入时，若 `checkStatus` 为 `CUST_CHECK_PASS` 或 `CUST_CHECK_REJECT` 且非变更广播，则直接跳过，避免重复处理，由工作流审核执行器统一处理。

## 需求背景

消息通知审核通过/驳回异步发送，不阻塞主流程。`CustSyncEventProvider.pushChangeAfterCommit` 使用事务后异步线程池执行；消息发送失败仅记录日志不抛出异常。

```ground:rule
name: "运营中台审批回调过滤规则"
content: "onEvent 收到 checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 且非变更广播时，直接跳过，由工作流审核执行器处理"
impact: "避免通过/拒绝事件被重复处理"
field_targets:
  - "cust_company_info.check_status"
evidence: "code_path:CustSyncEventProvider.onEvent"
```

```ground:claim
claim: "消息通知审核通过/驳回异步发送，不阻塞主流程"
evidence: "code_path:CustSyncEventProvider.pushChangeAfterCommit + reqdoc:claim-6"
```

## 版本演进

暂无。

相关：[[cust_company_info]]
