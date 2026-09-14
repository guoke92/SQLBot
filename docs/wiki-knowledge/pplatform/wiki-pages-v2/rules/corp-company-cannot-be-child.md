---
type: rule
title: 集团公司不可作为子级
page_key: corp-company-cannot-be-child
domain: 企业集团关系
status: draft
aliases: [集团角色互斥, CORPORATION_COMPANY]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - code_path:CustGroupRelApplication.java:processCompany
contract_version: "0.1"
belong: rules
---

角色互斥规则：已经是集团公司的企业不能被设置为其他公司的子级；导入场景中根企业必须是集团角色。相关口径见 [[calibers/group-root-node]] 与 [[processes/cust-group-rel-status-state]]。

## 需求背景

集团树是一棵有向树，若允许集团企业再成为别人的子级会产生跨集团的环与权限冲突；导入场景下根节点角色不符时无法自动创建，只能提示联系运营补建。

## 版本演进

v0 契约按现状固化，判断依据为企业角色字段（含 CORPORATION_COMPANY）。

## 规则锚点

```ground:rule
name: 集团公司不可作为子级
content: 目标企业 cust_company_type 含 CORPORATION_COMPANY 时抛“该企业已是集团公司，无法设置为其他公司的子级企业”；导入时根企业必须是集团角色，否则提示联系运营添加。
impact: 集团角色互斥
field_targets:
  - cust_company_info.cust_company_type
  - cust_group_rel.cust_type
evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel / processCompany
```