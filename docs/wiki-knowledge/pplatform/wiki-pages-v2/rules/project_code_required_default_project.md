---
type: rule
title: 项目码必填联动默认项目
page_key: rule.project_code_required_default_project
domain: 租户配置
status: draft
aliases:
  - 项目码必填
  - projectCodeRequired
  - defaultProjectId 必填
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:checkBeforeSave
contract_version: "0.1"
---

当租户配置了 `projectCodeRequired='Y'`（即 [[calibers/project_code_required_tenant]]），保存前必须同时提供 `defaultProjectId`，否则直接抛错阻断保存。`defaultProjectId` 指向 [[tables/tenant_project]]，因此该规则把「项目码必填」的租户与一个默认项目强绑定，避免出现要求项目码却没有默认项目可回的悬空配置。

## 需求背景

以项目码作为业务主键的租户在创建业务单据时必须能回落到一个默认项目；若只开必填开关而不绑定默认项目，会在业务提交环节才暴露问题，因此把校验前移到租户保存。

## 版本演进

v0.1：依据 `checkBeforeSave` 中的前置校验建立规则；`field_targets` 中第二项在语义分析来源中被截断，暂未登记，待补证后回填。

```yaml
rule: 项目码必填联动默认项目
content: "projectCodeRequired='Y' 时 defaultProjectId 必须非空，否则抛「项目码为必填时，请先配置默认关联项目」"
impact: 阻断租户保存
field_targets:
  - tenant_setting_config.project_code_required
```

相关页面：[[tables/tenant_setting_config]]、[[tables/tenant_project]]、[[calibers/project_code_required_tenant]]、[[processes/tenant_status_effective]]。