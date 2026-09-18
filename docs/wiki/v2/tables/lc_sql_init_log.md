---
type: table
title: 蜂搭插件sql执行记录
page_key: lc_sql_init_log
belong: tables
status: draft
anchors: [lc_sql_init_log]
sources: ['database_schema:lowcode_pplatform.lc_sql_init_log']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
---

# 蜂搭插件sql执行记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`

### 未归簇

`name`, `description`

## 字段

```ground:table
table: lc_sql_init_log
database: lowcode_pplatform
description: 蜂搭插件sql执行记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [name]
clusters:
- key: common
  title: 通用
  include: always
fields:
- name: id
  data_type: number
  nullable: false
  cluster: common
- name: name
  data_type: string
  description: 插件名称
  nullable: false
- name: description
  data_type: string
  description: sql文本
```
