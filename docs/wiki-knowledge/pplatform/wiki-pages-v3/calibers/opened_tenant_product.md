---
type: caliber
title: 已开通租户通用产品
page_key: opened_tenant_product
domain: 租户产品/互通产品/租户项目
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
  - tenant_product.open_status
---

租户层已开通。不要和企业 OPENED 混用。

```ground:caliber
name: 已开通租户通用产品
predicate: "tenant_product.open_status = 'Y'"
scope: tenant_product
evidence: code
```
