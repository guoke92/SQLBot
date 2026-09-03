---
type: concept
title: 客户迁移
page_key: customer_migration
domain: 租户迁移
status: published
aliases: [迁移客户]
oid: 15
maps_to: "tenant_migarory_log.type = 'migratoryCust'"
field_targets: [tenant_migarory_log.type]
adjudication: boundary
also_confused_with: [migratoryOnTheWayCust]
boundary: "migratoryCust 为普通存量客户迁移；migratoryOnTheWayCust 为在途客户迁移"
sources: [db, code, "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：客户迁移指存量客户数据迁移。

## 需求背景
迁移客户登录后弹出平台升级提示（已证实）。AMS 与讯易链存量企业需数据合并（已证实）。

## 版本演进
v0.1 基于 DB 类型字段与术语桥边界定义。

关联：[[customer_migration_success]] [[customer_migration_redis_lock]] [[ams_enterprise_merge]]

相关：[[tenant_migarory_log]]
