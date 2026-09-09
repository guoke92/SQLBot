---
type: caliber
title: 迁移日志成功
page_key: migratory_log_success
belong: calibers
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

# 迁移日志成功

业务定位：用于标识迁移或同步成功的日志记录。

## 需求背景

当 `tenant_migarory_log.status = 'Y'` 时，表示该批次或该次迁移/同步已成功完成。该口径用于统计成功率或过滤成功记录。

## 版本演进

暂无。

```ground:caliber
name: 迁移日志成功
predicate: tenant_migarory_log.status = 'Y'
scope: 迁移/同步成功记录
evidence: db:tenant_migarory_log.status distribution Y=144694
```

相关：[[tenant_migarory_log]]
