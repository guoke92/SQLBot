---
type: caliber
title: 已推送创建事件的租户
page_key: calibers.pushed-created-event-tenant
domain: tenant-config-operation-email
status: published
aliases: [已推送创建事件的租户, pushing_status=Y]
oid: 1
sources: [code]
contract_version: "0.1"
field_targets: [tenant_setting_config.pushing_status]
scope:
  databases: [lowcode_pplatform]
---

该口径标记租户是否已成功推送过 CREATE 事件，是控制后续非 CREATED 事件推送顺序的前置条件。

## 需求背景

租户信息推送需要保证 CREATE 事件优先于 UPDATE 等其他事件，因此系统通过 `pushing_status='Y'` 判断是否允许推送后续事件。

## 版本演进

- 初版（v0.1）：由 `TenantAppliactionService.pushTenant` 使用该口径控制推送顺序。

```ground:caliber
name: 已推送创建事件的租户
predicate: "tenant_setting_config.pushing_status = 'Y'"
scope: 允许推送非CREATED事件的前置条件
evidence: "code:TenantAppliactionService.pushTenant"
```

[[tenant_setting_config]]