---
type: concept
title: 运营人员(租户级)
page_key: concept.tenant_operator
domain: 租户配置
status: draft
aliases:
  - operator_id
  - operator_name
  - operator_email
  - 运营人
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
maps_to: tenant_setting_config.operator_id / operator_name / operator_email
field_targets:
  - tenant_setting_config.operator_id
  - tenant_setting_config.operator_name
  - tenant_setting_config.operator_email
adjudication: boundary
also_confused_with:
  - opContactA
  - cust_person_info.operator_id
sources: ["enrich:wiki-admin"]
---

「运营人员」在系统里存在于三个层级，本概念只指租户级：[[tables/tenant_setting_config]] 的 `operator_id` / `operator_name` / `operator_email`，用于运营邮件触达（配合 `send_email`，并由 `op_update_user` / `op_update_time` 记录运营配置的更新轨迹）。项目级对应 [[concepts/op_contact_a]] 等 `tenant_project.op_contact_*`；企业联系人级对应 [[tables/cust_person_info]] 的 `operator_id` / `operator_realname` / `operator`。三者不可混用，运营邮件的最终收件人需按层级叠加判断。

## 需求背景

租户级运营人承担面向整个租户的运营邮件触达；项目级对接人承担具体项目的协作；企业联系人级运营人用于追溯联系人归属。层级不同，责任范围与变更频率都不同。

## 版本演进

v0.1：确立与 `opContactA`、`cust_person_info.operator_id` 的边界裁决（boundary）。

相关：[[tenant_setting_config]]
