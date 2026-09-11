---
type: concept
title: 变更项编码
page_key: concept.item-code
domain: 企业变更与运营变更
status: draft
aliases: [item_code, 变更项, UN00xx]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_cfg
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
maps_to: cust_change_cfg.item_code
field_targets: [cust_change_cfg.item_code]
adjudication: boundary
also_confused_with: [cust_change_record.alter_type_id, cust_change_record.alter_data]
sources: ["enrich:wiki-admin"]
---

「变更项编码」指配置表 [[tables.cust_change_cfg]] 上的 `item_code`（DB 实测 `UN0001`–`UN0016`），是稳定的业务编码，也是对外与跨系统沟通变更项时使用的标识。变更单 [[tables.cust_change_record]] 上另有两个易混字段：`alter_type_id` 存的是配置表主键 `cust_change_cfg.id` 的逗号分隔串，必须 join 配置表才能还原为 `item_code`；`alter_data` 存的是 `item_code` 的 JSON 数组快照。

## 需求背景

变更项需要跨平台侧与运营中台侧对齐，因此用业务编码而非自增主键做语义标识；变更单保存主键列表是为了关联配置，保存编码数组是为了留存发起时的快照。识别管理员手机号变更项使用的正是编码，见 [[calibers.admin-phone-change-item]]。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

相关：[[cust_change_cfg]]
