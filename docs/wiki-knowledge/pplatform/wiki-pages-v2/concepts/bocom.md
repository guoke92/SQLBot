---
type: concept
title: 交e保
page_key: concepts/bocom
domain: CA证书收费
status: draft
aliases: [BOCOM]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeePaymentApplication.java
contract_version: "0.1"
maps_to: ca_fee_order.pay_method = 'BOCOM'
field_targets:
  - ca_fee_order.pay_method
  - ca_fee_order.bocom_txn_sts
adjudication: synonym
also_confused_with: [银行转账]
sources: ["enrich:wiki-admin"]
---

# 交e保

## 业务定位

**交e保**是当前 CA 服务费的**唯一支付渠道**（对公打款），在[[tables/ca_fee_order]]中以 `pay_method='BOCOM'` 标识。围绕它的关键字段包括：交易状态 `bocom_txn_sts`、平台流水号 `bocom_plfm_ser_no`、平台业务编号 `bocom_plfm_bsn_id`、请求流水号 `bocom_req_sn`。

**同义词**：`BOCOM`。

**易混边界**：交e保 ≠ **银行转账**。二者虽同为对公付款，但交e保走平台化接口与流水号回执，业务上需要按交易状态判成功/失败/待查证——对应口径[[calibers/bocom_success]]（`00`）、[[calibers/bocom_failure]]（`01`）、[[calibers/bocom_pending_investigation]]（`02`）。**待查证（02）不等于失败**，不可直接并入失败口径。

支付发起的前置条件见[[rules/payment_precondition_rule]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段与代码枚举。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

相关：[[ca_fee_order]]
