---
type: enum
title: project_open_status
page_key: project_open_status
domain: 项目报表/统计/上报
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---





[[tables/cust_project_rel|cust_project_rel]].project_open_status 表示关联企业维度上的项目开通状态，DB 中实际分布有 NOT_OPEN 与 OPENED 两个字面值。

## 需求背景

需求文档未单列该枚举；值点来自 DB 分布。

## 版本演进

v0 契约首版，两个值点 verdict=correct，无 Java 枚举类承载。

```ground:enum
enum: project_open_status
fields: [cust_project_rel.project_open_status]
values:
  "NOT_OPEN":
    label: "未开通"
    note: "DB分布有NOT_OPEN和OPENED"
  "OPENED":
    label: "已开通"
    note: "DB分布有NOT_OPEN和OPENED"
```