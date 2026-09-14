---
type: concept
title: 灰度背景
page_key: gray_background
domain: 租户配置
status: draft
aliases:
  - 灰色背景
  - G
  - ColorConstants.GRAY
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
maps_to: "tenant_setting_config.bg_color = 'G'"
field_targets:
  - tenant_setting_config.bg_color
adjudication: synonym
also_confused_with: []
sources: ["enrich:wiki-admin"]
belong: concepts
---

「灰度背景」「灰色背景」「G」「ColorConstants.GRAY」指同一件事：[[tables/tenant_setting_config]] 中 `bg_color='G'` 所表达的灰色展示态。它是同义集合，不引入新的字段；筛选口径见 [[calibers/gray_bg_tenant]]，取值流转见 [[processes/bg_color_gray]]。

## 需求背景

灰度窗口期间前端需要统一的灰阶展示，业务与代码中对该状态的叫法不一，需要收敛为同一术语。

## 版本演进

v0.1：判定为同义词（synonym），不涉及字段边界争议。

相关：[[tenant_setting_config]]
