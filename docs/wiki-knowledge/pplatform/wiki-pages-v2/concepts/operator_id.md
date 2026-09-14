---
type: concept
title: 运营人员 / 运营对接人
page_key: operator_id
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [operatorId, operator_id, opContactA, operationId, 运营人员, 运营对接人]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AssetOperatorSyncApplication.syncAssetOperator；operCustFacade.getOperatorList"
contract_version: "0.1"
maps_to: cust_person_info.operator_id
field_targets:
  - cust_person_info.operator_id
adjudication: boundary
also_confused_with:
  - operation_user.operation_id
  - tenant_setting_config.operator_id
  - cust_project_rel.op_contact_a
belong: concepts
field_targets: [cust_person_info.operator_id]
---

「运营人员 / 运营对接人」在联系人侧指 [[cust_person_info]].operator_id，存的是运营中台人员 id（用 `operCustFacade.getOperatorList` 返回的 OperUserDTO.id 比对），不是本地表主键。

边界：cust_person_info.operator_id 是运营中台人员 id；operation_user.operation_id 是运营中台库内主键；tenant_setting_config.operator_id 是租户级运营人员；cust_project_rel.op_contact_a 是项目/企业关联表上的对接人字段。四者分属不同层，做关联时必须先确认所查表的语义。

## 需求背景
运营人员主数据在运营中台维护，业务侧只保存其 id 引用；跨库关联不能误用本地主键或关联表对接人字段。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。