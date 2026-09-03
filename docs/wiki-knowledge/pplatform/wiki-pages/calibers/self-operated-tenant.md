---
type: caliber
title: 自营租户
page_key: calibers.self-operated-tenant
domain: tenant-config-operation-email
status: published
aliases: [自营租户, 自营判定]
oid: 1
sources: [code, "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [tenant_setting_config.db_tenant_code, tenant_setting_config.tenant_flg_en]
scope:
  databases: [lowcode_pplatform]
---

自营租户口径用于判断租户是否为平台自营，通过项目标识与配置中的自营标识或平台数据租户编码进行匹配。

## 需求背景

某些业务逻辑需要区分自营与第三方租户，例如运营邮件发送或特殊处理，因此需要统一的自营判定口径。

## 版本演进

- 初版（v0.1）：由 `TenantAppliactionService.isLlsTenant` 实现该判定。

```ground:caliber
name: 自营租户
predicate: "tenant_setting_config.tenant_flg_en = tenantProperties.llsTenantFlgEn OR tenant_setting_config.db_tenant_code = tenantProperties.platformTenantDbTenantCode"
scope: 自营租户判定
evidence: "code:TenantAppliactionService.isLlsTenant"
```

[[tenant_flg_en]] [[数据租户标识]]

相关：[[tenant_setting_config]]
