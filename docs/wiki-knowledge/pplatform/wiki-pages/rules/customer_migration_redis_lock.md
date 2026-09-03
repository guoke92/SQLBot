---
type: rule
title: 企业迁移防重入锁
page_key: customer_migration_redis_lock
domain: 租户迁移
status: published
aliases: [Redis锁防重入]
oid: 19
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：防止同一企业并发迁移重复写入。

## 需求背景
迁移过程中需保证企业数据写入唯一性。

## 版本演进
v0.1 基于代码证据。

```ground:rule
name: 企业迁移防重入锁
content: migratoryCust 以 dbTenantCode_companyName_socialUnifiedCode 作为 lockName 获取 Redis 锁，未获取到锁抛 SyncException；finally 释放锁
impact: 防止同一企业并发迁移重复写入
field_targets: [cust_company_info, migratory_user_record]
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

关联：[[customer_migration]] [[cust_company_info]] [[migratory_user_record]]