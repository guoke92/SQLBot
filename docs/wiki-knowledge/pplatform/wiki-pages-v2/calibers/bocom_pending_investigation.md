---
type: caliber
title: 交e保划扣待查证
page_key: calibers/bocom_pending_investigation
domain: CA证书收费
status: draft
aliases: [bocom_txn_sts=02, 划扣待查证]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 交e保划扣待查证

## 业务定位

以[[tables/ca_fee_order]]的 `bocom_txn_sts='02'` 判定，表示交e保（[[concepts/bocom]]）侧**划扣结果尚未确定**，需要人工或后续对账查证。这是一类独立的中间态：既不能计入[[calibers/bocom_success]]，也不能计入[[calibers/bocom_failure]]。

对账场景下本口径是**待处理工作队列**；在收入统计中则应单列，避免资金口径错报。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 交e保划扣待查证
predicate: "ca_fee_order.bocom_txn_sts = '02'"
scope: ca_fee_order
evidence: code
```