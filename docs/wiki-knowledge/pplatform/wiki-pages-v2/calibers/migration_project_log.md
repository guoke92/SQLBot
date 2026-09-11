---
type: caliber
title: 迁移项目类型日志
page_key: migration_project_log
domain: 租户迁移
status: draft
aliases: [项目迁移日志口径, migratoryProject 日志]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---

项目迁移监控的取数口径：在 [[tenant_migarory_log]] 中同时接受操作类型 `migratoryProject` 与事件名称“迁移项目”。

```ground:caliber
name: 迁移项目类型日志
predicate: "tenant_migarory_log.type = 'migratoryProject' OR tenant_migarory_log.name = '迁移项目'"
scope: 项目迁移监控
evidence: "db:值分布"
```

## 需求背景

与租户迁移口径同构，术语等价关系见 [[migratory_project]]。需求文档中另有关于“定制项目标识/租户与定制项目映射表”的主张，目前无代码证据，不在本口径内展开，见 [[migratory_project]] 的版本演进说明。

## 版本演进

- v0（草稿）：口径来自 db 值分布；未区分项目迁移与项目同步（`PROJECT_SYNC`）。

关联页面：[[tenant_migarory_log]]、[[migratory_project]]、[[migration_log_success]]。