---
type: process
title: 互通产品开通
page_key: tenant_interworking_product__open_status
belong: processes
domain: tenant
status: draft
anchors: [tenant_interworking_product.open_status]
field_targets: [tenant_interworking_product.open_status]
sources: ['code_path:TenantInterworkingProductDomainService.java:246', 'code_path:TenantInterworkingProductDomainService.java:178']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_interworking_product]
---

# 互通产品开通

钉 tenant_interworking_product.open_status。active 写 Y，cancel 写 N。
取消不检查生效项目，不要和 tenant_product 取消规则混用。


```ground:process
process: 互通产品开通
field: tenant_interworking_product.open_status
entry: POST /app-web/tenantInterworkingProduct/cmd/active
stages:
- stage: 开通
  transitions:
  - from: N
    event: active
    to: Y
    evidence: code_path:TenantInterworkingProductDomainService.java:246
- stage: 取消
  transitions:
  - from: Y
    event: cancel
    to: N
    evidence: code_path:TenantInterworkingProductDomainService.java:178
```

## 页面链接

- [[tables/tenant_interworking_product]]
- [[dicts/tenant_interworking_product__open_status]]
