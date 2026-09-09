---
type: caliber
title: 租户迁移失败口径
page_key: tenant_migration_failure
belong: calibers
domain: 租户迁移
status: published
aliases: [租户迁移失败]
oid: 8
sources: [db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：统计租户迁移失败数量。

## 需求背景
需要按租户/批次统计迁移失败数，用于异常监控。

## 版本演进
v0.1 基于 DB 字段谓词。

```ground:caliber
name: 租户迁移失败口径
predicate: tenant_migarory_log.type = 'migratoryTenant' AND tenant_migarory_log.status = 'N'
scope: 按租户/批次统计迁移失败数
evidence: db
```

关联：[[tenant_migration]] [[tenant_migarory_log]]