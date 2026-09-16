---
type: enum
title: cust_product_active
page_key: cust_product_active
domain: 自动审核与工作流审核
status: draft
aliases: [开通中, 已开通产品]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [cust_product_active_flow, cust_interworking_active_flow]
---

# cust_product_active

`CustProductActiveConstant`：NOT_OPENED 未开通 / OPENING 开通中（注释含带客户确认） / OPENED 已开通。绑在企业开通表，不是租户 Y/P/N。

```ground:enum
enum: cust_product_active
fields:
  - cust_auth_application.open_status
  - cust_interworking_product.open_status
values:
  "NOT_OPENED":
    label: "未开通"
  "OPENING":
    label: "开通中"
  "OPENED":
    label: "已开通"
```
