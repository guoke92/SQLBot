---
type: rule
title: 集团删除前在途业务校验
page_key: root-group-delete-check
domain: 企业集团关系
status: draft
aliases: [removeRootGroup, 集团解散校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:removeRootGroup
contract_version: "0.1"
belong: rules
---

集团解散/移除成员前的约束规则：先扁平化整棵集团树做在途业务校验，通过后批量删除关系、释放额度并回收待办。相关表见 [[tables/cust_group_rel]]。

## 需求背景

集团关系中可能挂有额度等业务，直接删除会产生孤儿额度与在途业务，因此删除前必须逐节点校验。未生效且认证成功的子节点同时消除待办，避免遗留悬挂任务（参见 [[rules/notice-only-build-success]]）。

## 版本演进

v0 契约按现状固化，删除流程包含「校验—删关系—取消额度—消待办」四步。

## 规则锚点

```ground:rule
name: 集团删除前在途业务校验
content: removeRootGroup 先扁平化整棵集团树，调用 CheckGroupMemberDeleteService：额度模块 custWithActiveLimit 非空即抛 HAS_BUSINESS_PROCESS(有在途业务不允许删除)，再批量按主键删除关系并调用 limitFacade.cancelCustLimit；未生效且认证成功的子节点同时消除待办。
impact: 集团解散/成员移除约束
field_targets:
  - cust_group_rel.id
  - cust_group_rel.status
  - cust_company_info.cust_build_status
evidence: code_path:CustGroupRelApplication.java:removeRo
```