---
type: caliber
title: 已生效租户
page_key: calibers.activated-tenant
domain: tenant-config-operation-email
status: published
aliases: [已生效租户, status生效租户]
oid: 1
sources: [code]
contract_version: "0.1"
field_targets: [tenant_setting_config.enable, tenant_setting_config.status]
scope:
  databases: [lowcode_pplatform]
---

已生效租户口径用于筛选启用且业务生效（status=Y）的租户，区别于仅逻辑启用的租户。

## 需求背景

租户列表查询需要只展示已经通过生效条件的租户，避免未生效租户进入业务操作范围。

## 版本演进

- 初版（v0.1）：由 `TenantDomainService.listActicveAll` 应用该口径。

```ground:caliber
name: 已生效租户
predicate: "tenant_setting_config.enable = 'Y' AND tenant_setting_config.status = 'Y'"
scope: 生效租户列表
evidence: "code:TenantDomainService.listActicveAll"
```

[[任务状态]] [[tenant_setting_config]]