---
type: process
title: 租户生效状态（tenant_setting_config.status）
page_key: process.tenant_status_effective
domain: 租户配置
status: draft
aliases:
  - 租户生效状态
  - 待生效转已生效
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.status
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:effective
contract_version: "0.1"
---

租户配置的「生效」是一条单向人工推进的状态：新租户落在 `N`（待生效/未生效，存量中占多数），只有 `effective` 的必填项校验全部通过后才置为 `Y`。是否算作「生效租户」需要 `status='Y'` 与 `enable='Y'` 两个条件并列，见 [[calibers/effective_tenant]]；其中的必填项之一即项目码与默认项目的联动，见 [[rules/project_code_required_default_project]]。

## 需求背景

租户创建时往往缺少统一社会信用证编码、默认项目、平台运营方企业等前置信息，因此不能立即对外提供服务，需要「待生效」态承接配置补全，再由运营触发生效。生效门槛由校验项控制，避免未配置完整的租户进入可用列表。

## 版本演进

v0.1：登记当前代码中的状态取值与唯一一条 N→Y 迁移（必填项校验通过）。

```yaml
state_machine: 租户生效状态
field: tenant_setting_config.status
states:
  - value: "N"
    label: 待生效/未生效
    source: db_dist
  - value: "Y"
    label: 已生效
    source: db_dist
transitions:
  - from: "N"
    event: effective 必填项校验全部通过
    to: "Y"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:effective"
```

相关页面：[[tables/tenant_setting_config]]、[[calibers/effective_tenant]]、[[rules/project_code_required_default_project]]。