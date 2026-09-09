---
type: rule
title: 批量变更运营人员记录规则
page_key: rule_batch_change_operator
belong: rules
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustPersonApplication.batchChangeOperator", "CustPersonApplication.changeOperator", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_oper_change_record.change_reason, cust_oper_change_record.change_type]
coverage_note: 运营人员变更
scope:
  databases: [lowcode_pplatform]
---

该规则规定运营人员变更时的审计记录方式：批量导入采用 `BATCH` 类型，原因固定为“批量变更运营人员”；单人变更采用 `MANUAL` 类型，原因固定为“手动变更运营人员”，保证审计追踪的一致性。

## 需求背景

暂无特定需求声明。

```ground:rule
name: "批量变更运营人员记录规则"
content: "批量导入变更运营人员时，记录 changeType=BATCH，changeReason=批量变更运营人员；单人变更记录 changeType=MANUAL，changeReason=手动变更运营人员"
impact: "运营变更审计追踪"
field_targets:
  - "cust_oper_change_record.change_type"
  - "cust_oper_change_record.change_reason"
evidence: "code_path:CustPersonApplication.batchChangeOperator / changeOperator"
```

## 版本演进

暂无。

相关：[[cust_oper_change_record]]
