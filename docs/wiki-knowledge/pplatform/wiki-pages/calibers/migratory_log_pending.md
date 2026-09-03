---
type: caliber
title: 迁移日志待处理
page_key: migratory_log_pending
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [tenant_migarory_log.status]
scope:
  databases: [lowcode_pplatform]
---

# 迁移日志待处理

业务定位：用于标识迁移或同步失败或待处理的日志记录。

## 需求背景

当 `tenant_migarory_log.status = 'N'` 时，表示该批次或该次迁移/同步尚未成功，可能处于失败或待处理状态。该口径用于监控异常或待重试记录。

## 版本演进

暂无。

```ground:caliber
name: 迁移日志待处理
predicate: tenant_migarory_log.status = 'N'
scope: 迁移/同步失败或待处理记录
evidence: db:tenant_migarory_log.status distribution N=7362
```

相关：[[tenant_migarory_log]]
