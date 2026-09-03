---
type: table
title: 蜂搭插件sql执行记录
page_key: lc_sql_init_log
domain: 基线
status: draft
anchors: [lc_sql_init_log]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 蜂搭插件sql执行记录

（基线页：3 字段，行数估计 4。行语义/常用过滤待语义摄取增强。）

```ground:table
table: lc_sql_init_log
database: lowcode_pplatform
desc: 蜂搭插件sql执行记录
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(20)
  - name: description
    type: string
    phys: varchar(1024)
    desc: sql文本
  - name: name
    type: string
    phys: varchar(100)
    desc: 插件名称
    topk: 2|3|a|b
```
