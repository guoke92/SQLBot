---
type: rule
title: 迁移企业防重复同步锁
page_key: company_sync_lock
domain: 租户迁移
status: draft
aliases: [企业重复同步锁, dbTenantCode+companyName+socialUnifiedCode 锁]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
contract_version: "0.1"
belong: rules
---

本规则用于挡住同一次企业信息的重复同步：以数据租户编码、企业名称、统一社会信用代码三者拼接作为锁标识，取锁失败即判定为重复同步并抛错，从而保证企业迁移的幂等性。

```ground:rule
name: 迁移企业防重复同步锁
content: 迁移企业信息时，使用 Redis 锁，锁 key 由 dbTenantCode + companyName + socialUnifiedCode 拼接，若获取锁失败则抛出重复同步异常。
impact: 数据一致性
field_targets:
  - redis:lockName
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

## 需求背景

该规则是 [[ams_company_merge]] 的前置保护：并发的企业迁移请求会在锁层被拒绝，避免同一企业在合并分支上被并发改写。锁粒度由业务三要素决定，而非请求编号，说明设计意图是“企业维度”去重。

## 版本演进

- v0（草稿）：规则来自代码证据 `PlatFormMigratoryApplication.java:migratoryCust`；锁过期与释放策略未在证据中体现，待确认。

关联页面：[[ams_company_merge]]、[[migratory_cust]]、[[migration_cust_log]]。