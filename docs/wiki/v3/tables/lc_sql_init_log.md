---
type: table
title: 蜂搭插件sql执行记录
page_key: lc_sql_init_log
belong: tables
status: draft
anchors:
- lc_sql_init_log
sources:
- database_schema:lowcode_pplatform.lc_sql_init_log
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related: []
---
# 蜂搭插件sql执行记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: lc_sql_init_log
database: lowcode_pplatform
desc: 蜂搭插件sql执行记录
inactive: false
primary_key:
- id
grain: 低代码 SQL 初始化日志（catalog 有表；pplatform-web 无 @TableName DO）
name_anchors:
- name
fields:
- name: id
  type: number
  nullable: false
- name: name
  type: string
  desc: 插件名称
  nullable: false
- name: description
  type: string
  desc: sql文本
```

## 页面链接
