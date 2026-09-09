---
type: caliber
title: 租户迁移成功口径
page_key: tenant_migration_success
belong: calibers
domain: 租户迁移
status: published
aliases: [租户迁移成功]
oid: 7
sources: [db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：统计租户迁移成功数量。

## 需求背景
需要按租户/批次统计迁移成功数，支撑迁移监控。

## 版本演进
v0.1 基于 DB 字段谓词。

```ground:caliber
name: 租户迁移成功口径
predicate: tenant_migarory_log.type = 'migratoryTenant' AND tenant_migarory_log.status = 'Y'
scope: 按租户/批次统计迁移成功数
evidence: db
```

关联：[[tenant_migration]] [[tenant_migarory_log]]