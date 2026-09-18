---
type: rule
title: 互通产品取消不校验生效项目
page_key: interworking_cancel_skips_project_check
belong: rules
domain: tenant
status: draft
field_targets: [tenant_interworking_product.open_status]
sources: ['code_path:TenantInterworkingProductDomainService.java:178']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_interworking_product]
---

# 互通产品取消不校验生效项目

互通 cancel 直接写 open_status=N。不要套用 tenant_product 的 listEffectiveProjectByProduct 拒绝规则。

```ground:rule
rule: 互通产品取消不校验生效项目
field_targets: [tenant_interworking_product.open_status]
impact: write_constraint
content: 互通 cancel 直接写 open_status=N。不要套用 tenant_product 的 listEffectiveProjectByProduct
  拒绝规则。
evidence: code_path:TenantInterworkingProductDomainService.java:178
```

## 页面链接

- [[tables/tenant_interworking_product]]
- [[dicts/tenant_interworking_product__open_status]]
- [[processes/tenant_interworking_product__open_status]]
