---
type: caliber
title: 集团根节点口径
page_key: group-root-node
domain: 企业集团关系
status: draft
aliases: [集团本身, root_flag=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java:checkCustGroup
contract_version: "0.1"
belong: calibers
---

集团根节点指代表集团本身的关系记录，判定条件为 `cust_group_rel.root_flag = 'Y'`；root_flag = 'Y' 的企业不可签署成员单位协议，也不可作为子级被关联。字段边界见 [[concepts/root-flag]]。

## 需求背景

集团树必须有一个根来承载集团角色，根节点与成员单位在权限上互斥：根不能成为别人的子级，也不能以成员身份签署协议。相关准入校验见 [[rules/effective-member-no-op]] 与 [[rules/corp-company-cannot-be-child]]。

## 版本演进

v0 契约按现状固化；`level` 字段实测仅 1（根节点），层级能力尚未展开使用。

## 口径锚点

```ground:caliber
name: 集团根节点
predicate: cust_group_rel.root_flag = 'Y'
scope: 根节点识别；root_flag=Y 的企业不可签成员单位协议
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```