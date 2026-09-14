---
type: rule
title: 推数白名单短路
page_key: push_whitelist_shortcut
domain: 租户迁移
status: draft
aliases: [推数白名单, platformPointServiceExcludeDbTenantCode]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#push"
  - "code:MigratoryPointServiceImpl.java#call"
contract_version: "0.1"
belong: rules
---

租户对应的数据租户标识命中白名单配置时直接 return，既不推送也不产生流水记录。口径见 [[push_whitelist_tenant]]。

```ground:rule
name: 推数白名单短路
content: "tenantId 对应租户 dbTenantCode 命中 platformPointServiceExcludeDbTenantCode 时直接 return，不产生推数记录"
impact: "灰度/隔离特定租户的推数"
field_targets:
  - tenant_migarory_log.db_tenant_code
evidence: "code:MigratoryPointServiceImpl.java#push,#call"
```

## 需求背景

迁移期部分租户的业务系统尚未具备接收能力，需按租户粒度暂停出向推数，且不留下失败流水以免污染重试池。

## 版本演进

由无差别推送演进为配置化白名单短路；短路不落流水，是排障时"查不到记录"的常见原因（见 [[failed_migratory_log]]）。

相关：[[同步]]、[[tenant_setting_config]]。