---
type: caliber
title: 需开通 CA 尚未开通
page_key: need_open_ca
domain: CA证书认证
status: draft
aliases: [待开通电子签章]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCompanyIfoEnchanceService.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
---

意愿为需要开通，且开通结论仍是未开通或开通中。列在 [[cust_company_info]]。`need_register_ca='N'` 的企业不进本口径。

```ground:caliber
name: 需开通 CA 尚未开通
predicate: "cust_company_info.need_register_ca = 'Y' AND cust_company_info.ca_register_status IN ('N', 'P')"
scope: cust_company_info
evidence: code
```
