---
type: caliber
title: 开通中企业产品
page_key: opening_cust_product
domain: 自动审核与工作流审核
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_auth_application.open_status
---

开通中（含待客户确认）。

```ground:caliber
name: 开通中企业产品
predicate: "cust_auth_application.open_status = 'OPENING'"
scope: cust_auth_application
evidence: code
```
