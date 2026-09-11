---
type: caliber
title: 未缴费企业
page_key: calibers/unpaid_company
domain: CA证书收费
status: draft
aliases: [UNPAID 企业, pay_status=UNPAID]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 未缴费企业

## 业务定位

以[[tables/ca_fee_company]]的 `pay_status='UNPAID'` 判定，是本域**欠费/待缴**的基准口径。服务到期处理会把企业置为 `UNPAID`（见[[processes/ca_fee_company_pay_status]]），因此该口径同时包含"从未缴费"与"已到期未续费"两类企业；**若业务只想看前者，需叠加服务期口径**（[[calibers/service_expired]]、[[calibers/in_service_period]]）进一步区分。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表字段取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 未缴费企业
predicate: "ca_fee_company.pay_status = 'UNPAID'"
scope: ca_fee_company
evidence: db
```