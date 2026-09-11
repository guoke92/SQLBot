---
type: rule
title: 运营人员变更记录查询口径
page_key: rule.oper-change-record-query
domain: 企业变更与运营变更
status: draft
aliases: [queryByPersonId, 运营变更历史查询]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
---

按 `person_id` 精确匹配、`enable='Y'`（见 [[calibers.oper-change-record-valid]]），按 `create_time` 倒序返回；`personId` 为空直接返回空列表。表见 [[tables.cust_oper_change_record]]，字段指代见 [[concepts.operator]]。

## 需求背景

联系人详情页展示运营变更历史时，只要当前绑定关系的历史轨迹，不要已失效行；空入参直接短路，避免全表扫描。倒序保证最新一次变更置顶。

## 版本演进

v0.1：首次登记，规则来自 `OperChangeRecordApplication.queryByPersonId`。

```ground:rule
name: 运营人员变更记录查询口径
content: 按 person_id 精确匹配、enable='Y'，按 create_time 倒序返回；personId 为空直接返回空列表
impact: 联系人详情页的运营变更历史列表
field_targets:
  - cust_oper_change_record.person_id
  - cust_oper_change_record.enable
  - cust_oper_change_record.create_time
evidence: code_path:OperChangeRecordApplication.java:queryByPersonId
```