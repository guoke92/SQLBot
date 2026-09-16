---
type: caliber
title: CA 已开通企业
page_key: ca_registered_company
domain: CA证书认证
status: draft
aliases: [ca_register_status=Y]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:cust_company_info"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [cust_company_info.ca_register_status]
---

列在 [[cust_company_info]]。需要开通但尚未开通见 [[need_open_ca]]。

```ground:caliber
name: CA 已开通企业
predicate: "cust_company_info.ca_register_status = 'Y'"
scope: cust_company_info
evidence: db
```
