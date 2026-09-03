---
type: concept
title: 客户角色状态
page_key: customer-role-status
domain: 客户角色与数据权限组织
status: published
aliases:
  - roleStatus
  - 角色状态
oid: 1
sources:
  - db
  - code
contract_version: "0.1"
maps_to: cust_role_info.status
field_targets:
  - cust_role_info.status
adjudication: boundary
also_confused_with:
  - 企业状态 cust_company_info.cust_status
  - 企业建档状态 cust_company_info.cust_build_status
  - 人员状态 cust_person_info.status
scope:
  databases: [lowcode_pplatform]
---

客户角色状态描述客户企业角色的生命周期状态，取值 ADD/EFFECT/FREEZE/WRITEOFF。

## 需求背景

需要将客户角色状态与企业状态、建档状态、人员状态区分开。cust_role_info.status 只表示角色状态，而企业状态和人员状态分别由其他字段承载。

## 版本演进

初始语义抽取版本，后续需补充状态机与其他实体状态的交叉约束。

相关页面：[[customer-role-status-machine]] [[cust_role_info]]