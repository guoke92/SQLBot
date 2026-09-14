---
type: concept
title: 集团（集团公司/根企业）
page_key: group_root
domain: 集团关系
status: draft
aliases:
  - root
  - rootGroup
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_group_rel.root_flag
field_targets:
  - cust_group_rel.root_flag
also_confused_with:
  - cust_company_info.cust_company_type
adjudication: boundary
belong: concepts
field_targets: [cust_group_rel.root_flag]
sources: ["enrich:wiki-admin"]
---

# 集团（集团公司/根企业）

口语中的“集团/根企业”在数据上通常指 `cust_group_rel.root_flag = 'Y'` 的关系节点，口径见 [[group_root_node]]。

## 需求背景

集团树的构建、成员查询与签署边界都以根节点为起点：根节点禁止再次签署/拒绝（[[root_group_no_operation]]），按根节点拉平整树用于删除前校验（[[member_remove_check_business]]）。

## 版本演进

- 代码 `showCustGroupTree` 先看企业角色再查关系，说明“是集团”这一判断在实现中由角色与关系联合决定。

## 边界（adjudication: boundary）

`root_flag='Y'` 是关系表上的根节点标记；`cust_company_info.cust_company_type` 含 `CORPORATION_COMPANY` 才是企业角色意义上的集团。`showCustGroupTree` 先看角色再查关系，二者需联合判断，不可互推。

相关：[[cust_group_rel]]
