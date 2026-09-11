---
type: table
title: lc_sql_init_log（插件 SQL 执行日志表）
page_key: table.lc_sql_init_log
domain: 平台内部服务对接
status: draft
aliases:
  - lc_sql_init_log
  - 插件SQL日志表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[lc_sql_init_log]
contract_version: "0.1"
---


记录插件（低代码扩展）执行 SQL 文本的日志表，用于排查内部服务对接过程中由插件代执行的 DDL/DML。

## 需求背景

本表 name 列虽命名为「插件名称」，但实测取值为 '2'/'3'/'a'/'b' 等测试脏数据，不能作为业务枚举口径使用；description 列才是真正承载 SQL 文本的字段（varchar(1024)）。任何按 name 做插件分类统计的尝试都缺乏证据支撑。

## 版本演进

v0：首次成页；name 的「插件名称」语义仅来自 DDL 注释，实测数据不支持该口径，故不产出对应枚举页。

```ground:table
table: lc_sql_init_log
database: lowcode_pplatform
desc: 蜂搭插件sql执行记录
fields:
  - name: id
    type: number
  - name: description
    type: string
    desc: sql文本
  - name: name
    type: string
    desc: 插件名称
```