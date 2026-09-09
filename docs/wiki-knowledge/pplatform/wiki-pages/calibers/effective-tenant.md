---
type: caliber
title: 有效租户
page_key: effective-tenant
belong: calibers
domain: tenant-config-operation-email
status: published
aliases: [有效租户, enable有效租户]
oid: 1
sources: [code, reqdoc]
contract_version: "0.1"
field_targets: [tenant_setting_config.db_tenant_code, tenant_setting_config.enable]
scope:
  databases: [lowcode_pplatform]
---

有效租户口径用于判定租户是否处于启用且具有指定数据租户编码的状态。该口径是租户查询的基准，确保只返回逻辑未删除且匹配数据租户标识的记录。

## 需求背景

租户查询场景需要过滤掉已删除或数据租户不匹配的记录，因此以 `enable='Y'` 和 `db_tenant_code` 精确匹配为判定条件。

## 版本演进

- 初版（v0.1）：`TenantDomainService.getFirstByDbTenantCode` 使用该口径查询单个租户，且采用跳过事务方式。

```ground:caliber
name: 有效租户
predicate: "tenant_setting_config.enable = 'Y' AND tenant_setting_config.db_tenant_code = ?"
scope: 租户查询基准
evidence: "code_path:TenantDomainService.getFirstByDbTenantCode + reqdoc:BR-002"
```

[[数据租户标识]] [[tenant_setting_config]]