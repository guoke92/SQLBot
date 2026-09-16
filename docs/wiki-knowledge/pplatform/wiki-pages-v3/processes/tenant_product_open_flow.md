---
type: process
title: 租户通用产品开通状态机
page_key: tenant_product_open_flow
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
  - tenant_product.open_status
---

钉在租户通用产品开通列（Y/P/N）。ACFLOW/ORDER 可先置 P 等回调。

```ground:process
name: 租户通用产品开通状态机
field: tenant_product.open_status
states:
  - value: N
    label: 未开通
    source: code_enum
  - value: P
    label: 开通中
    source: code_enum
  - value: Y
    label: 已开通
    source: code_enum
transitions:
  - from: N
    event: 租户开通
    to: Y
    evidence: "code_path:TenantProductDomainService.java:191"
  - from: N
    event: 待回调开通
    to: P
    evidence: "code_path:TenantProductApplication.java:331"
  - from: Y
    event: 取消开通
    to: N
    evidence: "code_path:TenantProductDomainService.java:106"
```
