---
type: caliber
title: 迁移租户类型日志
page_key: migration_tenant_log
domain: 租户迁移
status: draft
aliases: [租户迁移日志口径, migratoryTenant 日志]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
belong: calibers
---

租户迁移监控的最小集合：在 [[tenant_migarory_log]] 中，租户迁移既可能以操作类型 `migratoryTenant` 记录，也可能以事件名称“迁移租户”记录，因此口径必须双字段取并。

```ground:caliber
name: 迁移租户类型日志
predicate: "tenant_migarory_log.type = 'migratoryTenant' OR tenant_migarory_log.name = '迁移租户'"
scope: 租户迁移监控
evidence: "db:值分布"
```

## 需求背景

type 与 name 的双写是历史脏数据形态而非两种业务，术语层面的等价关系记录在 [[migratory_tenant]]。漏用 OR 条件会导致迁移租户量被系统性低估。

## 版本演进

- v0（草稿）：口径来自 db 值分布，未确认是否所有租户迁移记录都同时写满 type 与 name。

关联页面：[[tenant_migarory_log]]、[[migratory_tenant]]、[[migration_log_success]]。