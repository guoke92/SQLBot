---
type: concept
title: 租户迁移
page_key: tenant_migration
belong: concepts
domain: 租户迁移
status: published
aliases: [迁移租户]
oid: 13
maps_to: "tenant_migarory_log.type = 'migratoryTenant'"
field_targets: [tenant_migarory_log.type]
adjudication: boundary
also_confused_with: [TENANT_SYNC, TENANT_SYNC_VALIDATE]
boundary: "migratoryTenant 是迁移入口操作类型；TENANT_SYNC 是租户同步步骤中的同步动作"
sources: [db, code, "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：租户迁移指将租户及其数据迁移到目标环境，对应操作类型 migratoryTenant。

## 需求背景
租户迁移接口需调整，自营租户存储映射关系（document_claim，未证实）——该声明未在代码中证实，code_path 显示仅委托扩展点，未见自营租户映射落库。

## 版本演进
v0.1 基于 DB 类型字段与术语桥边界定义。

关联：[[tenant_migration_success]] [[tenant_migration_failure]] [[tenant_must_exist]]

相关：[[tenant_migarory_log]]
