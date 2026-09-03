---
type: caliber
title: 统码口径
page_key: certification_no_unified
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.certification_no, ca_fee_order.certification_no]
scope:
  databases: [lowcode_pplatform]
---

# 统码口径

业务定位：以统一社会信用代码（统码）作为企业收费维度的关联键，确保企业台账与订单之间的数据一致性。

## 需求背景

`ca_fee_company` 表按统码唯一，`ca_fee_order` 表也记录统码，二者通过统码关联，保证企业维度台账一统码一行。

## 版本演进

统码作为核心标识，后续所有扩展表都应遵循此关联口径。

```ground:caliber
name: 统码口径
predicate: "ca_fee_company.certification_no = ca_fee_order.certification_no"
scope: 企业维度台账一统码一行
evidence: "db:uk_cert_no + code:CaFeeLedgerQueryService"
```

[[ca_fee_company]] · [[ca_fee_order]] · [[certification_no]]