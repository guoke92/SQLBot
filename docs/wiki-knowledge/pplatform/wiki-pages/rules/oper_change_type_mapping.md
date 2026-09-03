---
type: rule
title: 运营人员变更记录中文映射规则
page_key: rule_oper_change_type_mapping
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["OperChangeRecordApplication", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_oper_change_record.change_type]
coverage_note: 运营人员变更
scope:
  databases: [lowcode_pplatform]
---

该规则提供 `change_type` 值到中文描述的映射，用于前端展示。代码中存在 `AUTO_ASSIGN`、`AUTO_UPDATE` 的映射，但数据库分布未出现，可能为预留或未启用值。

## 需求背景

暂无特定需求声明。

```ground:rule
name: "运营人员变更记录中文映射规则"
content: "changeType 值 MANUAL/BATCH/ASSET_AUDIT_SYNC/CUST_CHANGE_CALLBACK 分别映射为手动变更/批量变更/资产审核同步/企业变更回调；AUTO_ASSIGN/AUTO_UPDATE 在代码中有映射但 DB 未出现"
impact: "前端展示用"
field_targets:
  - "cust_oper_change_record.change_type"
evidence: "code_path:OperChangeRecordApplication"
```

## 版本演进

暂无。

相关：[[cust_oper_change_record]]
