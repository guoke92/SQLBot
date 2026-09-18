---
type: process
title: 租户产品开通
page_key: tenant_product__open_status
belong: processes
domain: tenant
status: draft
anchors: [tenant_product.open_status]
field_targets: [tenant_product.open_status]
sources: ['code_path:TenantProductDomainService.java:191', 'code_path:TenantProductDomainService.java:106']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_product]
---

# 租户产品开通

开通写 Y；取消开通写 N。有关联项目或企业已开通产品则拒绝取消。

```ground:process
process: 租户产品开通
field: tenant_product.open_status
entry: 租户开通产品
stages:
- stage: 开通
  transitions:
  - from: N
    event: create/open
    to: Y
    evidence: code_path:TenantProductDomainService.java:191
- stage: 取消
  transitions:
  - from: Y
    event: cancel
    to: N
    guards: 无生效项目且无企业开通该产品
    evidence: code_path:TenantProductDomainService.java:106
```

## 页面链接

- [[tables/tenant_product]]
- [[dicts/tenant_product__open_status]]
