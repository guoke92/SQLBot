---
type: concept
title: 企业角色
page_key: enterprise_role
domain: 集团关系
status: draft
aliases:
  - custType
  - companyType
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_group_rel.cust_type
field_targets:
  - cust_group_rel.cust_type
also_confused_with:
  - cust_company_info.cust_company_type
adjudication: boundary
belong: concepts
field_targets: [cust_group_rel.cust_type]
sources: ["enrich:wiki-admin"]
---

# 企业角色

关系维度上的企业角色落库为 `cust_group_rel.cust_type`，是 JSON 数组字符串（形如 `["CORE"]`），支持一条关系多角色逐条写入。

## 需求背景

角色决定成员单位在集团中的定位，导入时要求同一上级下所有成员单位角色一致，且与已存在上级企业角色一致（[[member_role_consistency]]）。

## 版本演进

- `cust_type` 采用 JSON 数组字符串存储而非单值，历史上支持过多角色；解析统计时需按数组处理。

## 边界（adjudication: boundary）

`cust_group_rel.cust_type` 限定该条关系下的角色（JSON 数组字符串，多角色逐条写入），`cust_company_info.cust_company_type` 是企业全局角色；导入校验要求两者一致，但两者不是同一个字段、也不总是同时存在。

相关：[[cust_group_rel]]
