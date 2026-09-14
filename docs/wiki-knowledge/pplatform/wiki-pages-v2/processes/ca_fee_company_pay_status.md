---
type: process
title: 企业缴费状态机
page_key: ca_fee_company_pay_status
domain: CA证书收费
status: draft
aliases:
  - 企业缴费状态
  - pay_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

企业缴费状态机作用于 [[ca_fee_company]] 的 `pay_status`，是**企业维度汇总状态**，必须与订单维度 `ca_fee_order.order_status` 区分：订单级未缴是 `PENDING`，企业级未缴汇总是 `UNPAID`（见 [[pending_payment]]、[[paid_payment]]）。

迁移只有两条：订单缴费成功时回写为 `PAID`；服务到期处理（`markServiceExpired`）时回落为 `UNPAID`，后者由续费与到期规则驱动，见 [[renewal_remind_expire]]。`UNPAID` 并不等价于「立刻需要缴费」——多项目放行与豁免规则（[[multi_project_pass]]、[[whitelist_exempt]]、[[defer_pay_exempt]]、[[already_paid_in_service]]）会先于收费结论生效。

## 需求背景

企业级状态的引入使台账统计与「已缴费／未缴费企业筛选」可直接基于一行完成，无需对订单表做聚合；同时作为规则引擎的快速判断依据。

## 版本演进

- v0（本页）：依据语义分析中的状态与迁移证据建立首版状态机。

```ground:process
name: 企业缴费状态
field: ca_fee_company.pay_status
states:
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: UNPAID
    label: 未缴费
    source: code_enum
transitions:
  - from: UNPAID
    event: 订单缴费成功回写企业缴费状态
    to: PAID
    evidence: code_path:CaFeeOrderService.java:450
  - from: PAID
    event: 服务到期处理 markServiceExpired
    to: UNPAID
    evidence: code_path:CaFeeRenewalService.java
```