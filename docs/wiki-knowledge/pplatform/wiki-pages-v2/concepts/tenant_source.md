---
type: concept
title: 租户来源
page_key: tenant_source
domain: 租户配置
status: draft
aliases:
  - source
  - 租户来源id
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.source
  - db:tenant_setting_config.source_id
contract_version: "0.1"
maps_to: tenant_setting_config.source / source_id
field_targets:
  - tenant_setting_config.source
  - tenant_setting_config.source_id
adjudication: boundary
also_confused_with: []
sources: ["enrich:wiki-admin"]
belong: concepts
---

`source` 标记租户由哪一个上游系统创建，实测值为 `ACFLOW` / `pplatform`；`source_id` 是对应上游系统中的记录 ID。二者成对使用：一个说明来源系统，一个说明来源主键。与 [[calibers/stack_tenant_data]]（`is_stack` 区分存量/新增）语义相邻但不同——来源说明「从哪来」，存量标记说明「是否历史数据」。

## 需求背景

租户可能由多个上游系统同步创建，需要可追溯来源系统与来源主键，以便回查与对账。

## 版本演进

v0.1：依据 `source` 实测取值建立术语基线。

相关：[[tenant_setting_config]]
