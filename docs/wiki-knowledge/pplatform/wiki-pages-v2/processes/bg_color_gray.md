---
type: process
title: 租户背景颜色/灰度（tenant_setting_config.bg_color）
page_key: process.bg_color_gray
domain: 租户配置
status: draft
aliases:
  - 背景颜色状态
  - 灰度状态
  - bgColor
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorNull
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:setColorlight
contract_version: "0.1"
---

租户端的背景色由 `bg_color` 单一字段表达三种取值：`L`（彩色）、`G`（灰色）、`null`（未设置，按彩色处理）。灰度是全局窗口行为：当全局灰度窗口生效时，已设彩色的租户被打成灰色、未设颜色的租户也按灰色展示；客户端主动恢复彩色时字段回到 `null`，运营显式设为彩色时写入 `L`。全局窗口本身的状态见 [[processes/global_bg_gray_switch]]，灰色租户的筛选口径见 [[calibers/gray_bg_tenant]]。

## 需求背景

需要在不改主题色、不改智能客服按钮色的前提下，对全量租户做临时性灰度（如纪念日），因此把灰度语义单独收敛到 `bg_color` 上，避免与 `main_theme_color`、`ai_resource_color` 混淆。

## 版本演进

v0.1：登记当前代码中可达的取值与四条颜色迁移路径。

```yaml
state_machine: 租户背景颜色/灰度
field: tenant_setting_config.bg_color
states:
  - value: "L"
    label: 彩色
    source: code_enum
  - value: "G"
    label: 灰色
    source: code_enum
  - value: "null"
    label: 未设置（按彩色处理）
    source: db_dist
transitions:
  - from: "null"
    event: 全局灰度窗口生效且租户未设颜色
    to: "G"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray"
  - from: "L"
    event: 全局灰度窗口生效
    to: "G"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray"
  - from: "G"
    event: 客户端恢复彩色(bgcolor/reset/light)
    to: "null"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorNull"
  - from: "null"
    event: setColorlight 设为彩色
    to: "L"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:setColorlight"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/bg_color]]、[[concepts/gray_background]]、[[processes/global_bg_gray_switch]]、[[calibers/gray_bg_tenant]]。