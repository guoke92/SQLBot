---
type: caliber
title: 联易融自营租户
page_key: caliber.lls_self_tenant
domain: 租户配置
status: draft
aliases:
  - 联易融自营租户
  - isLlsTenant
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:isLlsTenant
contract_version: "0.1"
---

自营租户由两个可配置常量界定：`db_tenant_code` 等于平台租户配置值，或 `tenant_flg_en` 等于联易融租户标识值。该口径是 SSO/DBAss 初始化的前置判断——非自营租户才执行初始化流程。判定依据同时落在 [[concepts/db_tenant_code]] 与 [[concepts/tenant_flg_en]] 两个术语上，体现了两字段在业务上的分叉。

## 需求背景

联易融自营租户由内部系统对接，不需要走外部租户的 SSO/DBAss 初始化，因此需要在初始化前把这类租户识别出来并短路。

## 版本演进

v0.1：依据 `isLlsTenant` 判定逻辑建立口径。

```yaml
caliber: 联易融自营租户
predicate: "tenant_setting_config.db_tenant_code = ${tenantProperties.platformTenantDbTenantCode} OR tenant_setting_config.tenant_flg_en = ${tenantProperties.llsTenantFlgEn}"
scope: 非自营租户才做 SSO/DBAss 初始化
evidence: "code:TenantAppliactionService.java:isLlsTenant"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/db_tenant_code]]、[[concepts/tenant_flg_en]]、[[calibers/shared_fake_tenant]]。