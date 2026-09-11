---
type: rule
title: 运营人员变更类型字典
page_key: rule.oper-change-type-dict
domain: 企业变更与运营变更
status: draft
aliases: [CHANGE_TYPE_DESC, 变更类型映射]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC
  - code_path:OperChangeRecordApplication.java:toVO
contract_version: "0.1"
---

`change_type` 取值 `MANUAL`/`BATCH`/`AUTO_ASSIGN`/`AUTO_UPDATE`/`ASSET_AUDIT_SYNC`/`CUST_CHANGE_CALLBACK`，前端展示名由 `CHANGE_TYPE_DESC` 映射，未命中时回显原值。取值集合见 [[processes.oper-change-type]]，流水表见 [[tables.cust_oper_change_record]]。

## 需求背景

运营人员变更来源持续增加，字典映射必须对未知值保持降级可读（回显原值），否则新增来源在前端会显示为空；该策略保证流水列表不丢数据。

## 版本演进

v0.1：首次登记，规则来自 `OperChangeRecordApplication.CHANGE_TYPE_DESC` / `toVO`。

```ground:rule
name: 运营人员变更类型字典
content: change_type 取值 MANUAL/BATCH/AUTO_ASSIGN/AUTO_UPDATE/ASSET_AUDIT_SYNC/CUST_CHANGE_CALLBACK，前端展示名由 CHANGE_TYPE_DESC 映射，未命中时回显原值
impact: 运营人员变更流水的分类展示
field_targets:
  - cust_oper_change_record.change_type
evidence: code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC / toVO
```