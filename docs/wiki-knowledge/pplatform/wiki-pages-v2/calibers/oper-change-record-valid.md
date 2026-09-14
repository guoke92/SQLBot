---
type: caliber
title: 有效运营人员变更记录
page_key: oper-change-record-valid
domain: 企业变更与运营变更
status: draft
aliases: [运营变更流水有效口径, enable=Y 流水]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
belong: calibers
---

运营人员变更流水的查询口径为 [[tables.cust_oper_change_record]] 上 `enable = 'Y'`，按联系人精确匹配后返回。完整查询行为见 [[rules.oper-change-record-query]]，术语边界见 [[concepts.oper-change-record]]。

## 需求背景

流水表用于对外展示历史，删除行会破坏审计连续性，因此以逻辑有效标记过滤；查询恒带该标记，保证列表与详情一致。

## 版本演进

v0.1：首次登记，口径来自 `OperChangeRecordApplication.queryByPersonId`。

```ground:caliber
name: 有效运营人员变更记录
predicate: "cust_oper_change_record.enable = 'Y'"
scope: 按联系人查询运营人员变更流水
evidence: code_path:OperChangeRecordApplication.java:queryByPersonId
```