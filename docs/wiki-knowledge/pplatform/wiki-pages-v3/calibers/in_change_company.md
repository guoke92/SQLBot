---
type: caliber
title: 变更中企业
page_key: in_change_company
domain: 企业变更与运营变更
status: draft
aliases: [cust_status=CHANGE]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:cust_company_info"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [cust_company_info.cust_status]
---

列在 [[cust_company_info]]。不要用变更单 `status` 去数企业。

```ground:caliber
name: 变更中企业
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: cust_company_info
evidence: db
```
