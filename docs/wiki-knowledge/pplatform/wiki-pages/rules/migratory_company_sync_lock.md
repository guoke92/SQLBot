---
type: rule
title: 迁移企业同步加分布式锁防重入
page_key: migratory_company_sync_lock
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 迁移企业同步加分布式锁防重入

业务定位：在迁移企业数据时，通过分布式锁防止同一企业被并发重复迁移，保证迁移幂等性。

## 需求背景

在 `migratoryCust` 迁移过程中，系统使用 `dbTenantCode_companyName_socialUnifiedCode` 作为锁键获取 Redis 锁，若获取失败则抛出 `SyncException`。此外，迁移企业时需同步统一社会信用代码/认证信息（`setCompany` 设置 `certificationNo`），确保企业认证数据完整。

## 版本演进

暂无。

```ground:rule
name: 迁移企业同步加分布式锁防重入
content: migratoryCust 按 dbTenantCode_companyName_socialUnifiedCode 获取 Redis 锁，获取失败抛 SyncException
impact: 防止同企业并发重复迁移
field_targets:
  - CustCompanyInfoDO.dbTenantCode
  - CustCompanyInfoDO.name
  - CustCompanyInfoDO.certificationNo
evidence:
  - "code_path:PlatFormMigratoryApplication.java:migratoryCust"
  - "code_path:PlatFormMigratoryApplication.java:setCompany + reqdoc:迁移企业需同步统一社会信用代码/认证信息"
```