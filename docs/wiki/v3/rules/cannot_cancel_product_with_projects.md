---
type: rule
title: 有生效项目则不能取消开通产品
page_key: cannot_cancel_product_with_projects
belong: rules
domain: tenant
status: draft
field_targets: [tenant_product.open_status, tenant_project.product_id]
sources: ['code_path:TenantProductDomainService.java:118']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_product, tenant_project]
---

# 有生效项目则不能取消开通产品

listEffectiveProjectByProduct 非空，或企业已开通该租户产品，则拒绝取消开通。

```ground:rule
rule: 有生效项目则不能取消开通产品
field_targets: [tenant_product.open_status, tenant_project.product_id]
impact: write_constraint
content: listEffectiveProjectByProduct 非空，或企业已开通该租户产品，则拒绝取消开通。
evidence: code_path:TenantProductDomainService.java:118
```

## 页面链接

- [[tables/tenant_product]]
- [[tables/tenant_project]]
- [[dicts/tenant_product__open_status]]
- [[processes/tenant_product__open_status]]
