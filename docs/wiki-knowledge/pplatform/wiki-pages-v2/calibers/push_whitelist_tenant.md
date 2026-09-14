---
type: caliber
title: 推数白名单租户
page_key: push_whitelist_tenant
domain: 租户迁移
status: draft
aliases: [推数白名单口径, platformPointServiceExcludeDbTenantCode]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#push"
  - "code:MigratoryPointServiceImpl.java#call"
contract_version: "0.1"
belong: calibers
---

用于灰度与隔离：命中白名单配置的数据租户在执行推数前直接 return，既不推送也不产生流水记录，因此该租户在 [[failed_migratory_log]] 与出向统计中都不可见。

```ground:caliber
name: 推数白名单租户
predicate: "tenant_setting_config.db_tenant_code = '<白名单值>'"
scope: "platformPointServiceExcludeDbTenantCode 命中的租户直接 return，不推数"
evidence: "code:MigratoryPointServiceImpl.java#push"
```

## 需求背景

迁移期间部分租户的业务系统尚未准备好接收出向数据，需要按租户粒度暂停推数而不影响其他租户。

## 版本演进

由代码内固定列表演进为配置项（`tenant_setting_config`）驱动；白名单命中无流水留痕，排障时须先确认配置再怀疑推送链路。