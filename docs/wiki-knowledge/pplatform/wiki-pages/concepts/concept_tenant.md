---
type: concept
title: 租户
page_key: concept_tenant
belong: concepts
domain: customer
status: published
aliases: ["tenant", "dbTenantCode", "db_tenant_code"]
oid: 1
sources: []
contract_version: "0.1"
maps_to: "数据隔离维度 tenant.db_tenant_code"
field_targets: []
adjudication: boundary
also_confused_with:
  - "品牌(bandName)"
boundary: "tenant是数据隔离，品牌是租户配置的品牌名称"
scope:
  databases: [lowcode_pplatform]
---

租户是数据隔离的核心维度，通过 `db_tenant_code` 字段区分，不同租户数据相互隔离。

## 需求背景

在AMS对接中，租户产品开通状态、数据权限均以租户维度控制。数据库级隔离通过 `db_tenant_code` 实现，代码中大量使用 `MetaDataThreadLocalConfig.setDbTenantCode` 切换租户上下文。

## 版本演进

概念来自代码证据，文档中关于数据权限的声明已与代码锚定，见 `tenant_setting_config` 表的 reqdoc_claim。