---
type: table
title: cust_group_rel（集团/企业树关系表）
page_key: table.cust_group_rel
domain: 平台内部服务对接
status: draft
aliases:
  - cust_group_rel
  - 集团关系表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_group_rel]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

描述企业之间的集团树形结构：当前企业、直接父企业、根企业的 id 与集团节点 id 双轨记录，并给出层级与根标识。

## 需求背景

总部/集团标识在 [[tables/cust_company_info]] 中以 head_company 表达，树形结构则落在本表；成员角色 cust_type 与企业的角色数组同源（见 [[concepts/company_role_bridge]]）。根节点 level 为 1，root_flag='Y'。

## 版本演进

v0：首次成页。

```ground:table
table: cust_group_rel
columns:
  - field: cust_id / parent_cust_id / root_cust_id
    meaning: "当前企业 / 直接父企业 / 集团根企业 id"
    evidence: code
  - field: parent_group_id / root_group_id
    meaning: "直接父集团节点 / 根集团节点 id（树形结构键）"
    evidence: code
  - field: cust_type
    meaning: "成员角色，JSON 数组字符串"
    evidence: code
  - field: status
    meaning: "生效状态 INEFFECTIVE/EFFECTIVE"
    evidence: code
  - field: root_flag
    meaning: "是否根节点 'Y'"
    evidence: code
  - field: level
    meaning: "层级，根节点为 1"
    evidence: code
```
## 关联表

- [[cust_company_info]]：cust_group_rel.root_cust_id → cust_company_info.id（java-eq:CustGroupRelApplication.java，suggested）
