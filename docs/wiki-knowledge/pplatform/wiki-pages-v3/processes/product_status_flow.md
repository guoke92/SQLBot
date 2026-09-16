---
type: process
title: 平台产品生效状态机
page_key: product_status_flow
domain: 平台产品配置
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
  - platform_product.product_status
---

`PlatformProduct.effective()` 把 `'0'` 写成 `'1'`。

```ground:process
name: 平台产品生效状态机
field: platform_product.product_status
states:
  - value: 0
    label: 待生效
    source: code_enum
  - value: 1
    label: 已生效
    source: code_enum
transitions:
  - from: 0
    event: 产品生效
    to: 1
    evidence: "code_path:PlatformProduct.java:96"
```
