---
type: caliber
title: 融资期限上限口径（max_financing_period）
page_key: financing_period_cap
domain: 租户产品
status: draft
aliases: [融资期限上限, max_financing_period]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_interworking_product
contract_version: "0.1"
belong: calibers
---

本口径描述融资期限上限的取值形态。[[tables/tenant_product]] 以月为单位混存纯数字与带「个月」后缀的文本，[[tables/tenant_interworking_product]] 则以「1-3年」区间形式表达，两张表的单位与粒度并不统一。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径影响期限展示与校验，读取前需先归一单位。

## 版本演进
- tenant_product 实测值 12/36/6/12个月/36个月/6个月/6-12个月/0 显示单位后缀与区间写法是后加的。
- tenant_interworking_product 的 1-3年 为区间语义，与数值上限不可直接比较。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 融资期限上限口径
fields:
  - table: tenant_product
    field: max_financing_period
    values: ["12", "36", "6", "12个月", "36个月", "6个月", "6-12个月", "0"]
    definition: DB 实测 12/36/6/12个月/36个月/6个月/6-12个月/0
    evidence: db
  - table: tenant_interworking_product
    field: max_financing_period
    values: ["1-3年"]
    definition: DB 实测 1-3年 等
    evidence: db
```