---
type: rule
title: 批量白名单与延期规则
page_key: batch_whitelist_defer
domain: CA证书收费
status: draft
aliases:
  - 批量豁免
  - batchWhitelist
  - batchDefer
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerOperateService.java
contract_version: "0.1"
belong: rules
---

批量白名单写入项目 `WHITELIST`，同时**关闭 PENDING 订单**并创建 0 元已缴订单；批量延期写入 `DEFER_PAY`，并记录操作日志。该规则把运营决策转化为可追溯的订单事实，涉及 [[order_status_closed]]、[[whitelist]]、[[defer_pay_exempt]]。

## 需求背景

线下审批通过的白名单与延期必须落到系统且可审计，因此除了写配置，还要关闭既有待缴单并留痕，避免配置与订单状态不一致。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 批量白名单与延期规则
content: 批量白名单写入项目 WHITELIST，关闭 PENDING 订单并创建0元已缴订单；批量延期写入 DEFER_PAY，记录操作日志
impact: 运营后台批量豁免与延期
field_targets:
  - ca_fee_project_config.special_company_list
  - ca_fee_order.order_status
evidence: CaFeeLedgerOperateService.batchWhitelist/batchDefer
```