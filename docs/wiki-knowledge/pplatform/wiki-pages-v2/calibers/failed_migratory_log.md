---
type: caliber
title: 未成功推数/迁移记录
page_key: failed_migratory_log
domain: 租户迁移
status: draft
aliases: [待重试记录口径, status=N 流水]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:TenantMigaroryLogDaoImpl.java:87"
  - "db:tenant_migarory_log"
contract_version: "0.1"
belong: calibers
---

以默认值 N 表征的"待重试集合"（7426 条）。此口径同时是排查口径与重试口径，但仅与 [[outbound_push]] 取交集后才构成可重推集合。状态流转见 [[migratory_log_status]]。

```ground:caliber
name: 未成功推数/迁移记录
predicate: "tenant_migarory_log.status = 'N'"
scope: "默认值 N，作为待重试集合（7426 条）"
evidence: "db+code:TenantMigaroryLogDaoImpl.java:87"
```

## 需求背景

状态默认值必须能表达"未成功"，使回写失败、进程中断等异常天然落入待重试集合，避免漏推且无法发现。

## 版本演进

由显式写入失败状态演进为 DB 默认值 + 成功才回写 Y 的写法；同一字段的字典键来自 BooleanEnum，见 [[migratory_log_status]]。