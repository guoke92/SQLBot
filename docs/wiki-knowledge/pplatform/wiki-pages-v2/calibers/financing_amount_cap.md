---
type: caliber
title: 融资金额上限口径（max_financing_amount）
page_key: calibers/financing_amount_cap
domain: 租户产品
status: draft
aliases: [融资金额上限, max_financing_amount]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
contract_version: "0.1"
---

本口径描述 [[tables/tenant_product]] 中融资金额上限的取值形态，用于判断「限额」时上限以什么形式表达。是否限额本身见 [[calibers/financing_limit_flag]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该列同时存在数值与中文文本，意味着读取方需要按上下文决定按数值比较还是按文本展示。

## 版本演进
- 实测出现 0、88888888、不限 三类值：0 与「不限」在语义上冲突，88888888 疑似约定的「无穷大」，属历史兼容写法。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 融资金额上限口径
field: tenant_product.max_financing_amount
values: ["0", "88888888", "不限"]
definition: DB 实测 0/88888888/不限 等
evidence: db
```