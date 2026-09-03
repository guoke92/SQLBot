---
type: concept
title: 项目迁移
page_key: project_migration
domain: 租户迁移
status: published
aliases: [迁移项目]
oid: 14
maps_to: "tenant_migarory_log.type = 'migratoryProject'"
field_targets: [tenant_migarory_log.type]
adjudication: boundary
also_confused_with: [PROJECT_SYNC, syncProject]
boundary: "migratoryProject 对应批量迁移项目；syncProject/PROJECT_SYNC 为同步项目事件"
sources: [db, code, "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：项目迁移批量迁移项目。

## 需求背景
项目迁移存储定制项目标志（document_claim，未证实）——当前未在给定代码中证实该存储动作。

## 版本演进
v0.1 基于 DB 类型字段与术语桥边界定义。

关联：[[project_migration_success]] [[project_must_exist]]

相关：[[tenant_migarory_log]]
