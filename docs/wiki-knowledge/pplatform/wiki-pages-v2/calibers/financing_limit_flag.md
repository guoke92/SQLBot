---
type: caliber
title: 限额融资资金口径（max_financing_amount_flag）
page_key: financing_limit_flag
domain: 租户产品
status: draft
aliases: [是否限额融资资金上线, max_financing_amount_flag, 限额口径]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_interworking_product
contract_version: "0.1"
belong: calibers
---

本口径回答「某租户产品/互通产品是否对融资金额设上限」。[[tables/tenant_product]] 中该列 DB 实测为 Y/N/0/1 四种值，属布尔语义被多种写法混用；[[tables/tenant_interworking_product]] 中实测只有 N/Y 两值，形态更规范。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径被融资额度相关展示与校验复用，实际额度还要结合 [[calibers/financing_amount_cap]] 一起判断。

## 版本演进
- 0/1 与 N/Y 混存说明该列经历过布尔/字符两种表达方式的演进，统计时需先归一。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 是否限额融资资金上线口径
field: tenant_product.max_financing_amount_flag
values: ["Y", "N", "0", "1"]
definition: DB 实测 Y/N/0/1 混合值，N 为不限额，Y 为限额
evidence: db
```