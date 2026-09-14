---
type: caliber
title: 校验场景枚举（DB 实测）
page_key: funding_rule_detail_check_scene_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - check_scene 分布
  - 校验场景 SUBMIT_VALIDATE
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
contract_version: "0.1"
belong: calibers
---

[[funding_rule_detail]].check_scene 在库中只出现 SUBMIT_VALIDATE 一个取值。

## 需求背景

根据字段语义，本主题的 Application / Provider 写值点均未调用 setCheckScene，说明该列的写入方在其他链路（建单/校验链路），本页的取值分布不能推断为「本主题只支持一种场景」。写值点缺失已登记 REVIEW。

## 版本演进

v0 首次建立，计数取自 calibers 条目 DB 证据（实测 50 条）。

```ground:caliber
name: 校验场景枚举（DB 实测）
predicate: funding_rule_detail.check_scene = 'SUBMIT_VALIDATE'
scope: DB 实测 50 条，本主题代码未见写值点
evidence: db
```