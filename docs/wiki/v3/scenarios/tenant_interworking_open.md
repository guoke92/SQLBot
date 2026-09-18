---
type: scenario
title: 开通互通产品
page_key: tenant_interworking_open
belong: scenarios
domain: tenant
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_interworking_product, tenant_interworking_project]
---

# 开通互通产品

开通互通产品

```ground:scenario
scenario: tenant_interworking_open
hubs:
- table: tenant_interworking_product
  role: master
- table: tenant_interworking_project
  role: projects
lifecycle:
- dict: tenant_interworking_product__open_status
  process: tenant_interworking_product__open_status
```

## 页面链接

- [[tables/tenant_interworking_product]]
- [[tables/tenant_interworking_project]]
- [[dicts/tenant_interworking_product__open_status]]
- [[processes/tenant_interworking_product__open_status]]
