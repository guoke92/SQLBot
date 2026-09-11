---
type: caliber
title: 项目码必填租户
page_key: caliber.project_code_required_tenant
domain: 租户配置
status: draft
aliases:
  - 项目码必填租户
  - projectCodeRequired
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.project_code_required
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:checkBeforeSave
contract_version: "0.1"
---

`project_code_required='Y'` 的租户在保存前会进入更严格的校验分支：要求 `default_project_id` 非空，否则阻断保存（见 [[rules/project_code_required_default_project]]）。该口径与租户生效流程共同决定租户能否进入可用状态。

## 需求背景

部分租户以项目码作为业务主键，必须绑定默认项目才能创建业务单据，因此把「项目码必填」做成租户级开关而非全局规则。

## 版本演进

v0.1：依据 `checkBeforeSave` 的前置校验建立口径。

```yaml
caliber: 项目码必填租户
predicate: "tenant_setting_config.project_code_required = 'Y'"
scope: 保存前置校验要求 default_project_id 非空
evidence: "code:TenantDomainService.java:checkBeforeSave"
```

相关页面：[[tables/tenant_setting_config]]、[[rules/project_code_required_default_project]]、[[processes/tenant_status_effective]]。