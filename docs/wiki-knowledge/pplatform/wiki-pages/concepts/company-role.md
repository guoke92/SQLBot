---
type: concept
title: "企业角色"
page_key: company-role
domain: 集团与关联关系
status: published
aliases: ["custType", "companyType"]
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
maps_to: "cust_group_rel.cust_type 或 cust_company_info.cust_company_type"
field_targets: []
adjudication: boundary
also_confused_with: ["用户角色"]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

“企业角色”是企业维度的类型标识，用于区分集团、成员单位、核心企业等角色。企业角色存储为 JSON 数组字符串，可同时具有多种角色。

## 需求背景

- 企业角色不同于用户角色：用户角色是个人权限维度，企业角色是组织类型维度。

## 版本演进

- 暂无变更。

相关：[[cust_group_rel]] [[cust_company_info]] [[group]] [[member-unit]]