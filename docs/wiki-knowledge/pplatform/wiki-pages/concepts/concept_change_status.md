---
type: concept
title: 变更状态
page_key: concept_change_status
belong: concepts
domain: 企业变更与运营变更
status: published
aliases: ["status", "变更记录状态"]
oid: 1

sources: ["db_dist", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_change_record.status"
field_targets: ["cust_change_record.status"]
adjudication: "boundary"
also_confused_with: ["cust_company_info.check_status", "cust_company_info.cust_status"]
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“变更状态”指变更流程自身的状态，由 `cust_change_record.status` 承载。它描述一次变更申请从创建到审核、通过或驳回的推进阶段。

## 需求背景

业务上容易与企业的审核状态、客户生命周期状态混淆。边界如下：
- `cust_change_record.status` 表示变更流程自身的状态；
- `cust_company_info.check_status` 表示企业审核状态；
- `cust_company_info.cust_status` 表示企业生命周期状态（如 EFFECT/FREEZE/CHANGE）。

## 版本演进

暂无。

相关：[[cust_change_record]]
