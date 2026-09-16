---
type: caliber
title: 已开通企业产品
page_key: opened_cust_product
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

企业已开通的租户产品。不要用租户表 Y 或 CA 开通列代替。

```ground:caliber
name: 已开通企业产品
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: cust_auth_application
evidence: code
```
