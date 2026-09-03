---
type: caliber
title: 客户迁移成功口径
page_key: customer_migration_success
domain: 租户迁移
status: published
aliases: [客户迁移成功]
oid: 10
sources: [db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：统计客户迁移成功数量。

## 需求背景
需要按产品/批次统计客户迁移成功数。

## 版本演进
v0.1 基于 DB 字段谓词。

```ground:caliber
name: 客户迁移成功口径
predicate: tenant_migarory_log.type = 'migratoryCust' AND tenant_migarory_log.status = 'Y'
scope: 按产品/批次统计客户迁移成功数
evidence: db
```

关联：[[customer_migration]] [[tenant_migarory_log]]