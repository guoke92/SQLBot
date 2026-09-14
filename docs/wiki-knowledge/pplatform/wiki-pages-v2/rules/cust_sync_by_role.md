---
type: rule
title: 客户同步按角色维度规则
page_key: cust_sync_by_role
domain: 平台事件监听与同步
status: draft
aliases:
  - syncByRoleOn
  - 按角色同步广播
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncService.java:getRoles
  - code:CustSyncService.java:syncByRole
contract_version: "0.1"
belong: rules
---

同步广播的范围由 `syncByRoleOn` 决定：为 true 时同步企业全部角色，为 false 时只同步指定 `companyType` 对应的角色。

## 需求背景

每次同步前先 `MetaDataThreadLocalConfig.setDbTenantCode(dbTenantCode)` 切换租户上下文，见 [[db_tenant_code]]。角色维度的差异会直接影响经办人/管理员同步的分支走向，见 [[operator_sync_branch]]。

## 版本演进

- 租户上下文以 ThreadLocal 设置，若同一线程连续处理多租户批次，遗漏重置会串数据。

```ground:rule
name: 客户同步按角色维度
content: syncByRoleOn=true 时按企业全部角色同步，false 时仅同步指定 companyType 对应角色；每次同步先 MetaDataThreadLocalConfig.setDbTenantCode(dbTenantCode)
impact: 决定同步广播范围
field_targets: []
evidence: "code:CustSyncService.java:getRoles/syncByRole"
```