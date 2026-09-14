---
type: concept
title: 成员单位
page_key: member_unit
domain: 集团关系
status: draft
aliases:
  - 子企业
  - 子级企业
  - 上级企业
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_group_rel.cust_id
field_targets:
  - cust_group_rel.cust_id
also_confused_with:
  - cust_group_rel.parent_cust_id
adjudication: boundary
belong: concepts
field_targets: [cust_group_rel.cust_id]
sources: ["enrich:wiki-admin"]
---

# 成员单位

集团关系中的“成员单位”指当前这条关系挂靠的企业，落库为 `cust_group_rel.cust_id`；其上一级企业为 `parent_cust_id`。

## 需求背景

成员单位的增删改查、签署待办、删除前在途校验都围绕 `cust_id` 展开（[[member_remove_check_business]]、[[notice_no_duplicate]]），角色一致性校验见 [[member_role_consistency]]。

## 版本演进

- 关系表同时冗余 `root_cust_id`/`root_group_id`，成员查询可按根节点一次性拉平，减少递归。

## 边界（adjudication: boundary）

`cust_id` 是当前成员企业，`parent_cust_id` 是其上一级企业；两者同层级语义相反，建树/校验必须区分。口语中“上级企业”“子企业”在需求文档里都出现过，落到字段前必须先确认方向。

相关：[[cust_group_rel]]
