---
type: table
title: sys_cust_user_rel（企业—用户—角色—产品授权表）
page_key: table.sys_cust_user_rel
domain: 平台内部服务对接
status: draft
aliases:
  - sys_cust_user_rel
  - 授权关系表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[sys_cust_user_rel]
  - semantic:state_machines[经办人产品关联冻结状态]
contract_version: "0.1"
---

sys 服务侧的授权关系表，记录企业、用户、角色、产品四元关系及其冻结状态，是平台内部服务鉴权对接的落地表。

## 需求背景

冻结状态由 [[processes/operator_freeze_machine]] 描述：冻结经办人置 'Y'，解冻置 'N'。冻结同时会影响 [[tables/cust_person_info]] 的 enable 取值（见 [[rules/operator_permission_disable]]）。

## 版本演进

v0：首次成页。

