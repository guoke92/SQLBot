---
type: concept
title: 年费
page_key: annual_fee
belong: concepts
domain: ca_cert_fee
status: published
aliases: ["应缴年费"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_order.annual_fee / ca_fee_company.locked_annual_fee"
field_targets: ["ca_fee_order.annual_fee", "ca_fee_company.locked_annual_fee"]
adjudication: synonym
also_confused_with: []
boundary: "单位元；数据库 int(10) 存储"
scope:
  databases: [lowcode_pplatform]
---

# 年费

业务定位：CA 服务费的年度费用金额，单位元，存储为整数。

## 需求背景

年费分为订单层面的应缴年费和企业台账层面的锁定年费，两者语义一致，均表示年度服务费金额。

## 版本演进

当前金额为 int(10) 存储，未来可能支持小数或分单位。

[[ca_fee_order]] · [[ca_fee_company]] · [[rule_engine_exemption_chain]]