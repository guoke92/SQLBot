---
type: caliber
title: 迁移日志成功
page_key: migration_log_success
domain: 租户迁移
status: draft
aliases: [迁移成功口径, status=Y]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
belong: calibers
---

“迁移日志成功”把 [[tenant_migarory_log]] 的 status 取值收敛为可统计的成功集合，是迁移成功率、失败排查类指标的基数来源。

```ground:caliber
name: 迁移日志成功
predicate: "tenant_migarory_log.status = 'Y'"
scope: 迁移操作结果统计
evidence: "db:值分布"
```

## 需求背景

status 为单字符标志位，N 同时覆盖“未完成”与“失败”两种情形，因此“非成功”不等于“失败”，统计失败量时应显式排除未完成态——此边界目前只能依赖值分布观察，未在代码中找到状态写入分支，属待确认事项。

## 版本演进

- v0（草稿）：口径来自 db 值分布；未与 success_number / falied_number / total_number 三个计数列做交叉校验。

关联页面：[[tenant_migarory_log]]、[[migration_tenant_log]]、[[migration_project_log]]、[[migration_cust_log]]。