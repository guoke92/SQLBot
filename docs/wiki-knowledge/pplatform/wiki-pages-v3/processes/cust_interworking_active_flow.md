---
type: process
title: 企业互通产品开通状态机
page_key: cust_interworking_active_flow
domain: 租户产品/互通产品/租户项目
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - cust_interworking_product.open_status
---

与通用企业开通同一套 [[cust_product_active]]，钉在互通表。

```ground:process
name: 企业互通产品开通状态机
field: cust_interworking_product.open_status
states:
  - value: NOT_OPENED
    label: 未开通
    source: code_enum
  - value: OPENING
    label: 开通中
    source: code_enum
  - value: OPENED
    label: 已开通
    source: code_enum
transitions:
  - from: NOT_OPENED
    event: 企业开通互通产品
    to: OPENED
    evidence: "code_path:CustInterworkingProductDomainService.java:132"
```
