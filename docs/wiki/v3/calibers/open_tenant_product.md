---
type: caliber
title: 已开通租户产品
page_key: open_tenant_product
belong: calibers
domain: tenant
status: draft
field_targets: [tenant_product.open_status, tenant_product.enable]
sources: ['code_path:TenantProductDaoImpl.java:59']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_product, tenant_setting_config]
---

# 已开通租户产品

回答「租户已开通哪些产品」。开通中 P、未开通 N 排除。

```ground:caliber
caliber: 已开通租户产品
field_targets: [tenant_product.open_status, tenant_product.enable]
predicate: tenant_product.open_status = 'Y' AND tenant_product.enable = 'Y'
scope: global
boundary: 回答「租户已开通哪些产品」。开通中 P、未开通 N 排除。
using_relations:
- left: tenant_setting_config.id
  right: tenant_product.tenant_id
evidence: code_path:TenantProductDaoImpl.java:59
```

## 页面链接

- [[tables/tenant_product]]
- [[tables/tenant_setting_config]]
- [[dicts/tenant_product__enable]]
- [[dicts/tenant_product__open_status]]
- [[processes/tenant_product__open_status]]
