---
type: rule
title: 变更流程重建规则
page_key: rule_change_rebuild
belong: rules
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.changeRebuild", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_change_record.cust_id, cust_change_record.status]
coverage_note: 变更记录
scope:
  databases: [lowcode_pplatform]
---

该规则确保同一企业同一时间只存在一个在途变更流程。当发起新变更时，查询最新非终态变更记录，若无则抛异常；若有则调用运营中台 `changeRejectProcess` 拒绝旧流程，以重建新流程。

## 需求背景

需求曾主张“同一变更项同时只能有一个待审核的变更申请”，但代码实现按企业维度控制：查询最新非终态记录（按 `cust_id`），而非按变更项维度控制，因此实际为企业级串行而非变更项级。

```ground:rule
name: "变更流程重建规则"
content: "查询最新非终态变更记录（status 非 CUST_CHECK_PASS/REJECT），若无则抛异常；调用运营中台 changeRejectProcess 拒绝旧流程以重建新流程"
impact: "保证同企业同时只有一个在途变更流程"
field_targets:
  - "cust_change_record.status"
  - "cust_change_record.cust_id"
evidence: "code_path:CustChangeApplication.changeRebuild"
```

## 版本演进

暂无。

相关：[[cust_change_record]]
