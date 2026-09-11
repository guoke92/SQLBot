---
type: concept
title: 运营对接人A
page_key: concept.op_contact_a
domain: 租户配置
status: draft
aliases:
  - op_contact_a
  - opContactA
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_project.op_contact_a / cust_project_rel.op_contact_a / wec_project_operation_rel.op_contact_a
field_targets:
  - tenant_project.op_contact_a
  - cust_project_rel.op_contact_a
  - wec_project_operation_rel.op_contact_a
adjudication: boundary
also_confused_with:
  - operator_id
sources: ["enrich:wiki-admin"]
---

`opContactA` 是项目级运营对接人 A，取值为单个运营人员 ID，并同时落在项目主档与两处关联表上；更新时需要联动 `op_contact_a_group` 以保证分组一致。它与租户级/联系人级的 `operator_id` 属于不同维度（见 [[concepts/tenant_operator]]），不可互相赋值。同表的 `op_contact_b` 表示可多个运营人员ID的对接人B。

## 需求背景

一个项目按 A/B 双人对接运营是长期协作约定，关联表冗余保存是为了按客户、按项目两条检索路径都能直接命中对接人。

## 版本演进

v0.1：确立与 `operator_id` 的边界裁决（boundary），并登记三处落点。

相关：[[cust_project_rel]] [[tenant_project]] [[wec_project_operation_rel]]
