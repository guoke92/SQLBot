---
type: process
title: 租户推送状态（tenant_setting_config.pushing_status）
page_key: tenant_pushing_status
domain: 租户配置
status: draft
aliases:
  - 租户推送状态
  - pushingStatus
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.pushing_status
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:pushing
contract_version: "0.1"
belong: processes
---

`pushing_status` 是租户推送的前置开关：推送 CREATED 类型以外的租户事件之前，会先校验该字段是否已置 `Y`，从而保证「创建事件先于其他事件」的顺序约束。当前证据中只观测到 `Y`（已推送创建事件）一个取值，未推送一侧的显式取值未在证据中给出。

## 需求背景

租户事件存在顺序依赖：更新、生效等事件只有在创建事件成功推送后才有意义。用一个可由数据库直接判定的状态位替代跨系统查询，成本更低且可重放。

## 版本演进

v0.1：登记当前唯一有证据的取值与迁移路径。

```yaml
state_machine: 租户推送状态
field: tenant_setting_config.pushing_status
states:
  - value: "Y"
    label: 已推送创建事件
    source: code_enum
transitions:
  - from: "null"
    event: 推送 CREATED 租户事件前
    to: "Y"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:pushing"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/tenant_source]]。