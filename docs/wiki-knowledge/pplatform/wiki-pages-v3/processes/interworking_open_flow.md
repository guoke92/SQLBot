---
type: process
title: 租户互通产品开通状态机
page_key: interworking_open_flow
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
  - tenant_interworking_product.open_status
---

与通用租户开通同一 Y/P/N 字典，钉在互通表。

```ground:process
name: 租户互通产品开通状态机
field: tenant_interworking_product.open_status
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
    event: 开通互通产品
    to: Y
    evidence: "code_path:TenantInterworkingProductDomainService.java:246"
  - from: Y
    event: 取消开通
    to: N
    evidence: "code_path:TenantInterworkingProductDomainService.java:178"
```
