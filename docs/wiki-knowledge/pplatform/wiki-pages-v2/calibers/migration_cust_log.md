---
type: caliber
title: 迁移客户类型日志
page_key: migration_cust_log
domain: 租户迁移
status: draft
aliases: [客户迁移日志口径, migratoryCust 日志]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
belong: calibers
---

客户迁移监控的取数口径：在 [[tenant_migarory_log]] 中同时接受操作类型 `migratoryCust` 与事件名称“迁移客户”。

```ground:caliber
name: 迁移客户类型日志
predicate: "tenant_migarory_log.type = 'migratoryCust' OR tenant_migarory_log.name = '迁移客户'"
scope: 客户迁移监控
evidence: "db:值分布"
```

## 需求背景

本口径是 [[existing_user]]（存量用户）形成过程的观测入口：客户迁移动作同时会初始化 [[migratory_user_record]]，相关规则见 [[migratory_user_record_init]] 与 [[ams_company_merge]]。术语等价关系见 [[migratory_cust]]。

## 版本演进

- v0（草稿）：口径来自 db 值分布；与客户合并迁移（AMS 分支）的记录形态是否一致尚未验证。

关联页面：[[tenant_migarory_log]]、[[migratory_cust]]、[[ams_company_merge]]。