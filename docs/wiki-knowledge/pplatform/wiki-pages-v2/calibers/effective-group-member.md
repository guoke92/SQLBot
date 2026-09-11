---
type: caliber
title: 已生效集团成员单位口径
page_key: calibers/effective-group-member
domain: 企业集团关系
status: draft
aliases: [生效成员单位, status=EFFECTIVE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:listSubCust
contract_version: "0.1"
---

已生效集团成员单位指成员关系已完成确认的节点，判定条件为 `cust_group_rel.status = 'EFFECTIVE'`，作用域为平铺列表 / 子级列表（listSubCust）的过滤口径。

## 需求背景

集团树中包含未生效与已拒绝的关系记录（[[tables/cust_group_rel]]），对外展示与统计只应包含生效节点。状态的产生与流转见 [[processes/cust-group-rel-status-state]]，重复操作拦截见 [[rules/effective-member-no-op]]。

## 版本演进

v0 契约按现状固化，该口径与状态机三态基线一致。

## 口径锚点

```ground:caliber
name: 已生效集团成员单位
predicate: cust_group_rel.status = 'EFFECTIVE'
scope: 平铺/子级列表 listSubCust 过滤口径
evidence: code_path:CustGroupRelApplication.java:listSubCust
```