---
type: caliber
title: 迁移日志出站
page_key: migratory_log_outbound
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

# 迁移日志出站

业务定位：用于筛选数据从产融平台同步至下游业务系统的迁移日志记录。

## 需求背景

当 `tenant_migarory_log.direction = 'OUT'` 时，表示数据由产融平台向外同步。该口径用于追踪下行同步操作。

## 版本演进

暂无。

```ground:caliber
name: 迁移日志出站
predicate: tenant_migarory_log.direction = 'OUT'
scope: 数据同步至下游业务系统
evidence: db:tenant_migarory_log.direction distribution OUT=28984
```

相关：[[tenant_migarory_log]]
