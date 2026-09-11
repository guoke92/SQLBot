---
type: process
title: 企业缴费状态机
page_key: processes/ca_fee_company_pay_status
domain: CA证书收费
status: draft
aliases: [pay_status 状态机, 企业缴费状态流转]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - code:CaFeeRenewalService.java
contract_version: "0.1"
---

# 企业缴费状态机

## 业务定位

本页描述[[tables/ca_fee_company]]中 `pay_status` 的两态模型：`PAID`（已缴费）与 `UNPAID`（未缴费），是"企业当前是否欠费"的**最直接判据**，也是[[calibers/paid_company]]、[[calibers/unpaid_company]]两个统计口径的字段来源。

已证实的流转只有一条：**服务到期处理 `markServiceExpired` 将 `PAID` 置为 `UNPAID`**。反向的 `UNPAID → PAID`（即缴费成功回写）在本次语义分析中未见状态机条目，但其业务结果由[[processes/ca_fee_order_state]]中订单转 `PAID` 承载，请勿仅凭本页断言企业状态与订单状态必然同刻同步。

该状态不随时间自动回退：企业不欠费不等于服务仍在有效期内，判断"服务期内"须用[[calibers/in_service_period]]（`service_end >= CURDATE()`）。

## 需求背景

本页为代码侧状态流转的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。到期置为 `UNPAID` 与续费待办复位（[[processes/ca_fee_renew_remind]]）通常在同一次到期处理中被触发。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: 企业缴费状态机
field: ca_fee_company.pay_status
states:
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: UNPAID
    label: 未缴费
    source: code_enum
transitions:
  - from: PAID
    event: 服务到期处理 markServiceExpired
    to: UNPAID
    evidence: "code_path:CaFeeRenewalService.java:markServiceExpired"
```