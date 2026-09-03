---
type: process
title: 租户背景颜色
page_key: processes.tenant-bg-color
domain: tenant-config-operation-email
status: published
aliases: [租户背景颜色, tenant_setting_config.bg_color, 灰度颜色]
oid: 1
sources: [code_enum, db_dist, code]
contract_version: "0.1"
field_targets: [tenant_setting_config.bg_color]
scope:
  databases: [lowcode_pplatform]
---

租户背景颜色 `tenant_setting_config.bg_color` 支持 L（彩色）、G（灰色）与 null（未设置）三种状态。全局背景色开关与租户颜色的联动产生状态迁移，并辅以缓存机制。

## 需求背景

业务侧需要统一控制租户背景色视觉呈现，例如全局灰度期间租户背景置灰，过期后恢复未设置，或手动恢复彩色。同时系统通过 Redis 缓存灰度颜色开关以提升访问性能。

## 版本演进

- 初版（v0.1）：基于 `TenantAppliactionService` 的 updateTenantColorGray、updateTenantColorNull、setColorlight 实现状态迁移，具体行号未标。

```ground:process
name: 租户背景颜色
field: tenant_setting_config.bg_color
states:
  - value: L
    label: 彩色
    source: code_enum
  - value: G
    label: 灰色
    source: code_enum
  - value: null
    label: 未设置
    source: db_dist
transitions:
  - from: null
    event: updateTenantColorGray
    to: G
    evidence: "code_path:TenantAppliactionService.updateTenantColorGray:TenantAppliactionService.java:行号未标"
  - from: G
    event: updateTenantColorNull
    to: null
    evidence: "code_path:TenantAppliactionService.updateTenantColorNull:TenantAppliactionService.java:行号未标"
  - from: G
    event: setColorlight
    to: L
    evidence: "code_path:TenantAppliactionService.setColorlight:TenantAppliactionService.java:行号未标"
  - from: L
    event: updateTenantColorGray
    to: G
    evidence: "code_path:TenantAppliactionService.updateTenantColorGray:TenantAppliactionService.java:行号未标"
```

```ground:rule
name: 灰度颜色缓存
content: "灰度颜色缓存（ BR-003 ）：使用Redis缓存BGCOLOR_SWITCH_TTL，并处理过期降级"
evidence: "code_path:TenantSettingConfigController.getBgColor/setBgColor + reqdoc:BR-003"
```

[[bg_color]] [[tenant_setting_config]]