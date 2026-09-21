---
type: table
title: 蜂搭插件sql执行记录
page_key: lc_sql_init_log
belong: tables
status: draft
anchors: [lc_sql_init_log]
sources: ['database_schema:lowcode_pplatform.lc_sql_init_log']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [lc_sql_init_log__name]
---

# 蜂搭插件sql执行记录

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: lc_sql_init_log
database: lowcode_pplatform
desc: 蜂搭插件sql执行记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [name]
fields:
- name: id
  type: number
  nullable: false
- name: name
  type: string
  desc: 插件名称
  nullable: false
  dict: [a, b, '3', '2']
- name: description
  type: string
  desc: sql文本
```

## 页面链接

### 字典

- [[dicts/lc_sql_init_log__name]]（`lc_sql_init_log.name`）
