---
type: caliber
title: 已缴费企业
page_key: paid_company
domain: CA证书收费
status: draft
aliases: [PAID 企业, pay_status=PAID]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
belong: calibers
---

# 已缴费企业

## 业务定位

以[[tables/ca_fee_company]]的 `pay_status='PAID'` 判定。用于统计"当前无欠费"的企业规模。注意该口径为**企业维度的状态快照**，不保证订单侧存在对应的已支付单据（见[[calibers/paid_order]]），两者不可互相替代。其对偶口径见[[calibers/unpaid_company]]。

状态如何从 `PAID` 变为 `UNPAID` 见[[processes/ca_fee_company_pay_status]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表字段取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 已缴费企业
predicate: "ca_fee_company.pay_status = 'PAID'"
scope: ca_fee_company
evidence: db
```