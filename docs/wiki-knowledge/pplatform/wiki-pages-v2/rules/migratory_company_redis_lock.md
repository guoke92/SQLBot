---
type: rule
title: 迁移企业防重锁
page_key: migratory_company_redis_lock
domain: 租户迁移
status: draft
aliases: [迁移企业防重, 企业迁移锁]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
belong: rules
---

同一租户下同名同证件企业的迁移是串行化的：先抢 Redis 锁再落库，抢不到直接抛 `SyncException`（『迁移企业信息重复同步』），方法级事务回滚，不留半成品数据。锁键包含租户维度，见 [[tenant_code]]。

```ground:rule
name: 迁移企业防重锁
content: "迁移企业加 Redis 锁，key = dbTenantCode + '_' + companyName + '_' + socialUnifiedCode；获取失败直接抛 SyncException『迁移企业信息重复同步』，方法级 @Transactional 回滚"
impact: "保证同一租户下同名同证件企业不被并发/重复迁移"
field_targets:
  - cust_company_info.db_tenant_code
  - cust_company_info.name
  - cust_company_info.certification_no
evidence: "code:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

业务系统在迁移期可能重发迁移报文，产融侧必须保证幂等，不能产生两条企业主体或一条半成品主体。

## 版本演进

由数据库唯一约束兜底演进为 Redis 前置锁 + 事务回滚，减少无效写入与脏数据。

相关：[[cust_company_info]]、[[ams_migratory_dedup]]。