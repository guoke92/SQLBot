---
type: rule
title: 运营人员查询必须带 deleted 过滤
page_key: operation_user_deleted_filter
domain: 数据权限与组织
status: draft
aliases: [operation_user 删除过滤]
oid: 1
scope:
  databases: [base]
sources: [db]
contract_version: "0.1"
belong: rules
---

[[tables/operation_user]] 存在已删除数据（db 实测 deleted 分布为 N=119 / Y=22），因此对该表的任何查询都必须显式带 deleted 过滤条件，否则约 15% 的已删除运营人员会进入结果集。这是本表最容易被忽略的查询前置条件。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 db 字段语义直接得出。注意：语义分析只给出「查询必须带 deleted 过滤」这一要求，未给出保留值的具体约定（Y/N 哪一侧为有效），落地时需与调用方确认。

## 版本演进

v0：依据 db 证据成文。

```ground:rule
name: operation_user 逻辑删除过滤
statement: 查询 operation_user 必须带 deleted 过滤
condition: 任意对 operation_user 的读取
action: 过滤掉已删除记录（实测 N=119 / Y=22，存在已删除数据）
evidence: db
```