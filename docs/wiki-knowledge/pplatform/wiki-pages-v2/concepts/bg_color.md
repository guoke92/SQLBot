---
type: concept
title: bgColor
page_key: concept.bg_color
domain: 租户配置
status: draft
aliases:
  - 背景颜色
  - 灰度颜色
  - bg_color
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
maps_to: tenant_setting_config.bg_color
field_targets:
  - tenant_setting_config.bg_color
adjudication: boundary
also_confused_with:
  - main_theme_color
  - ai_resource_color
sources: ["enrich:wiki-admin"]
---

`bgColor` 只承载灰度开关语义，取值 `L`（彩色，ColorConstants.LIGHT）、`G`（灰色，ColorConstants.GRAY）、`null`（未设置，按彩色处理）。它不表达主题色，也不表达智能客服按钮色——`main_theme_color` 与 [[tables/tenant_setting_config]] 中的 `ai_resource_color` 各自独立。状态迁移见 [[processes/bg_color_gray]]，配套的全局窗口见 [[processes/global_bg_gray_switch]]。

## 需求背景

临时性全局灰度需要与常规配色解耦，避免灰度操作污染主题配置，因此把灰度收敛到单一字段上。

## 版本演进

v0.1：确立与 `main_theme_color`、`ai_resource_color` 的边界裁决（boundary）。

相关：[[tenant_setting_config]]
