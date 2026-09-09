---
type: rule
title: 背景色全局开关与租户背景色联动
page_key: bg-color-global-switch-rule
belong: rules
domain: tenant-config-operation-email
status: published
aliases: [背景色全局开关与租户背景色联动, updateTenantColorGray]
oid: 1
sources: [code]
contract_version: "0.1"
field_targets: [tenant_setting_config.bg_color]
scope:
  databases: [lowcode_pplatform]
---

该规则定义全局背景色生效期间如何联动修改租户 `bg_color`：全局生效置为 G，过期后置为 null，恢复彩色时置为 L。

## 需求背景

当平台开启全局灰度时，租户侧需要同步变为灰色；灰度结束需恢复未设置状态，或手动恢复彩色。该联动规则保证全局视觉一致性。

## 版本演进

- 初版（v0.1）：通过 `TenantAppliactionService` 的多个方法实现联动。

```ground:rule
name: 背景色全局开关与租户背景色联动
content: "全局背景色生效期间，租户bg_color置为G；过期后置为null；恢复彩色时置为L"
impact: 修改tenant_setting_config.bg_color
field_targets:
  - tenant_setting_config.bg_color
evidence: "code_path:TenantAppliactionService.updateTenantColorGray/updateTenantColorNull/setColorlight"
```

[[bg_color]] [[tenant-bg-color]] [[tenant_setting_config]]