---
type: caliber
title: 已缴费企业
page_key: paid_company
belong: calibers
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status]
scope:
  databases: [lowcode_pplatform]
---

已缴费企业口径用于从企业维度识别已经完成当期 CA 服务费缴费的企业。

## 需求背景

规则评估需要判断企业是否处于已缴费状态，以便在服务期内不被重复催缴，并作为服务有效性的参考。

## 版本演进

v0.1 草稿：基于数据库字段语义确定口径。

```ground:caliber
name: 已缴费企业
predicate: "ca_fee_company.pay_status = 'PAID'"
scope: 企业维度
evidence: db
```

相关：[[ca_fee_company]]、[[ca_fee_company_pay_status]]、[[fee_rule_priority_chain]]