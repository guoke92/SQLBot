---
type: concept
title: 交e保
page_key: bocom
belong: concepts
domain: CA证书收费与订单
status: published
aliases: ["BOCOM", "bocom"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_order.pay_method = 'BOCOM'"
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“交e保”是 CA 服务费的一种支付渠道，代码中常以 BOCOM/bocom 表示。其业务边界为支付渠道为交e保的订单。

## 需求背景

支付确认、台账编辑限制等规则需要识别交e保支付订单，并以其交易状态作为操作约束依据。

## 版本演进

v0.1 草稿：作为术语桥接建立，后续可补充交e保接口字段与状态码映射。

相关：[[ca_fee_order]]、[[bocom_payment_confirmation]]、[[ledger_edit_restrictions]]