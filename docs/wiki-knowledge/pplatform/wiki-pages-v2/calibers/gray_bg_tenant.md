---
type: caliber
title: 灰色背景租户
page_key: gray_bg_tenant
domain: 租户配置
status: draft
aliases:
  - 灰色背景租户
  - G 灰度租户
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:getTentantColorSet
contract_version: "0.1"
belong: calibers
---

客户端读取背景色时，以 `bg_color='G'` 识别灰色租户；该口径的生效前提是全局灰度窗口处于 ON（见 [[processes/global_bg_gray_switch]]）。注意 `bg_color` 为 `null` 的租户在窗口内也会被处理成灰色，但库内取值仍是 null，因此本口径只覆盖「已显式置灰」的租户。

## 需求背景

灰度窗口期间需要批量把彩色租户翻成灰色，并保留客户端可单方面恢复彩色的能力，因此「灰色」既可能来自库内取值也可能来自窗口计算，查询口径需要明确区分。

## 版本演进

v0.1：依据 `getTentantColorSet` 与 `bg_color` 取值分布建立口径。

```yaml
caliber: 灰色背景租户
predicate: "tenant_setting_config.bg_color = 'G'"
scope: 客户端背景色展示（灰度窗口内）
evidence: "code:TenantAppliactionService.java:getTentantColorSet"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/bg_color]]、[[concepts/gray_background]]、[[processes/bg_color_gray]]、[[processes/global_bg_gray_switch]]。