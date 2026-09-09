---
type: caliber
title: 迁移日志入站
page_key: migratory_log_inbound
belong: calibers
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [tenant_migarory_log.direction]
scope:
  databases: [lowcode_pplatform]
---

# 迁移日志入站

业务定位：用于筛选数据迁入产融平台的迁移日志记录。

## 需求背景

当 `tenant_migarory_log.direction = 'IN'` 时，表示数据从外部系统迁入产融平台。该口径常用于统计入站迁移量或监控入站流程。

## 版本演进

暂无。

```ground:caliber
name: 迁移日志入站
predicate: tenant_migarory_log.direction = 'IN'
scope: 数据迁入产融平台
evidence: db:tenant_migarory_log.direction distribution IN=123072
```

相关：[[tenant_migarory_log]]
