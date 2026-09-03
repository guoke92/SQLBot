---
type: concept
title: 变更项编码
page_key: concept_item_code
domain: 企业变更与运营变更
status: published
aliases: ["itemCode"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_change_cfg.item_code"
field_targets: ["cust_change_cfg.item_code"]
adjudication: "boundary"
also_confused_with: ["alter_type_id", "alter_type"]
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“变更项编码”是配置表中定义的变更项唯一标识，存于 `cust_change_cfg.item_code`。它在变更申请中被引用，用于精确匹配可变更项。

## 需求背景

边界说明：`item_code` 是配置表中的变更项编码；`alter_type_id` 是变更记录中关联的配置 ID 列表；`alter_type` 是变更类型描述。

## 版本演进

暂无。

相关：[[cust_change_cfg]]
