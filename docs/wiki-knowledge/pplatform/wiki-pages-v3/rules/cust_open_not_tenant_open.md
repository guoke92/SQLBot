---
type: rule
title: 企业开通不是租户开通
page_key: cust_open_not_tenant_open
domain: 自动审核与工作流审核
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - cust_auth_application.open_status
  - tenant_product.open_status
---

企业开通 NOT_OPENED/OPENING/OPENED；租户开通 Y/P/N。同名「已开通」键不同。CA 开通另见 ca_register_status。

```ground:rule
name: 企业开通不是租户开通
content: 企业开通 NOT_OPENED/OPENING/OPENED；租户开通 Y/P/N。同名「已开通」键不同。CA 开通另见 ca_register_status。
field_targets: [cust_auth_application.open_status, tenant_product.open_status]
evidence: "code_path:CustProductActiveConstant.java:11"
```
