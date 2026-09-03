---
type: concept
title: "成员单位"
page_key: member-unit
domain: 集团与关联关系
status: published
aliases: ["子公司", "子级企业"]
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
maps_to: "cust_group_rel 中 parent_group_id 不为空的记录"
field_targets: []
adjudication: boundary
also_confused_with: ["供应商", "经销商"]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

“成员单位”是集团树中的非根节点，通过 `parent_group_id` 关联到父关系节点。成员单位的角色由 `cust_type` 决定，不同于供应商或经销商。

## 需求背景

- 成员单位是集团树中的非根节点。
- 其企业角色可能为多种，但与供应商、经销商属于不同业务维度。

## 版本演进

- 暂无变更。

相关：[[group]] [[cust_group_rel]] [[company-role]]