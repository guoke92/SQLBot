---
type: rule
title: 运营变更记录查询口径
page_key: oper_change_query
domain: 企业变更与运营变更
status: draft
aliases: [queryByPersonId, 运营变更历史查询]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
belong: rules
---

规则内容：按 `person_id` 查询且 `enable='Y'`（[[valid_oper_change_record]]），按 `create_time` 倒序；`change_type` 经 `CHANGE_TYPE_DESC` 映射为中文描述，`operatorId`/`operatorName` 取自 `createBy`/`createUser`。

## 需求背景

运营人员变更历史要求最新的在最前，且对外展示中文字面量与操作者名称，因此查询层固定排序与字段映射。

## 版本演进

v0.1：首次固化查询与展示映射。

```ground:rule
name: 运营变更记录查询口径
content: "按 person_id 查询且 enable='Y'，按 create_time 倒序；change_type 经 CHANGE_TYPE_DESC 映射为中文描述，operatorId/operatorName 取自 createBy/createUser"
impact: 运营人员变更历史展示
field_targets:
  - cust_oper_change_record.person_id
  - cust_oper_change_record.enable
  - cust_oper_change_record.change_type
evidence: "code_path:OperChangeRecordApplication.java#queryByPersonId/#toVO"
```

相关页面：[[cust_oper_change_record]]、[[valid_oper_change_record]]、[[operator]]、[[cust_person_info]]。