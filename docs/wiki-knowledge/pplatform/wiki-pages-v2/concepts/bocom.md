---
type: concept
title: 交e保
page_key: bocom
domain: CA证书收费
status: draft
aliases:
  - 交e保对公打款
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to: ca_fee_order.pay_method
field_targets:
  - ca_fee_order.pay_method
  - ca_fee_order.bocom_txn_sts
adjudication: boundary
boundary: pay_method 表示支付渠道；bocom_txn_sts 表示该渠道划扣响应状态
also_confused_with:
  - ca_fee_order.bocom_txn_sts
belong: concepts
field_targets: [ca_fee_order.pay_method]
sources: ["enrich:wiki-admin"]
---

「交e保」是当前代码主要支持的支付方式，落到 `ca_fee_order.pay_method = 'BOCOM'`；其划扣结果由同表的 `bocom_txn_sts`（`00`／`01`／`02`）与平台流水 `bocom_plfm_ser_no`、业务编号 `bocom_plfm_bsn_id`、请求流水 `bocom_req_sn` 承载。

**边界（易混淆）**：`pay_method` 回答「走哪个渠道」，`bocom_txn_sts` 回答「这个渠道这次划扣的结果如何」。相关口径见 [[bocom_txn_sts_00]]、[[bocom_txn_sts_01]]、[[bocom_txn_sts_02]]；幂等与查证逻辑见 [[bocom_idempotent_verify]]。

## 需求背景

对公打款需与银行侧对账，故需要独立的渠道响应状态与多组流水号，以便补单、查证与幂等拦截。

## 版本演进

- v0（本页）：建立术语桥与边界。

相关：[[ca_fee_order]]
