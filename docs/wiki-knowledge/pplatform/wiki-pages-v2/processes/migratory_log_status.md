---
type: process
title: 推数/迁移记录处理状态机
page_key: migratory_log_status
domain: 租户迁移
status: draft
aliases: [推数记录状态机, tenant_migarory_log.status 状态机]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:TenantMigaroryLogDaoImpl.java:87"
  - "code:MigratoryPointServiceImpl.java#pushByLog"
  - "db:tenant_migarory_log"
contract_version: "0.1"
belong: processes
---

流水行的处理状态：落库默认 N，`logOut` 回写 BooleanEnum 字典键置 Y；未成功的行不会被自动丢弃，而是作为重试池由 `pushByLog` 按 `reqNo` 再推一次。相关口径：[[failed_migratory_log]]、[[outbound_push]]、[[push_whitelist_tenant]]。

```ground:process
name: 推数/迁移记录处理状态
field: tenant_migarory_log.status
states:
  - value: N
    label: "未成功/待重试（DB 默认 N）"
    source: db_dist
  - value: Y
    label: "处理成功"
    source: db_dist
transitions:
  - from: N
    event: "推数执行并 logOut 回写（BooleanEnum 字典键）"
    to: Y
    evidence: "code_path:TenantMigaroryLogDaoImpl.java:87"
  - from: N
    event: "按 reqNo 重新推送 pushByLog（仅 direction=OUT 且非 *_SYNC_VALIDATE）"
    to: Y
    evidence: "code_path:MigratoryPointServiceImpl.java#pushByLog"
```

## 需求背景

迁移/推数期业务系统偶发不可用，失败记录必须可追溯且可重放；重放必须幂等（同一 `req_no` 不产生重复推送），且不得把入向迁移记录与出向校验器记录纳入重推范围。

## 版本演进

状态值从多状态收敛为布尔语义（BooleanEnum 字典键 Y/N），DB 默认值 N 使"漏回写"天然进入待重试集合；重推入口统一收敛到 `pushByLog`。