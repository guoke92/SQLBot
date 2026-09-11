---
type: concept
title: 平台运营方
page_key: concept.platform_operator
domain: 租户配置
status: draft
aliases:
  - platform_operator
  - platformOperator
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.platform_operator
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/component/PlatformComponentFacade.java:needPlatformOperatorCompany
contract_version: "0.1"
maps_to: tenant_setting_config.platform_operator(JSON数组)
field_targets:
  - tenant_setting_config.platform_operator
adjudication: boundary
also_confused_with: []
sources: ["enrich:wiki-admin"]
---

`platform_operator` 以 JSON 数组存储，元素取值 `platform` / `tenant`，可组合。它的判定是「包含」而非「等于」：仅当数组含 `platform` 时才要求运营方企业存在，见 [[calibers/platform_operator_configured]]。因此「配置了平台运营方」与「需要校验运营方企业」不是等价条件。

## 需求背景

平台运营与租户方运营是两种运营主体，校验条件与业务前置不同，故用可组合数组表达，避免为两种组合各建字段。

## 版本演进

v0.1：登记 JSON 数组语义与「包含 platform」判定口径。

相关：[[tenant_setting_config]]
