---
type: scenario
title: 开通租户产品
page_key: tenant_product_open
belong: scenarios
domain: tenant
status: draft
aliases: [租户开通产品]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_product, tenant_setting_config]
---

# 开通租户产品

每租户每平台产品一行。open_status=Y 才算开通。有项目则不能取消。

```ground:scenario
scenario: tenant_product_open
hubs:
- table: tenant_product
  role: master
shared:
- table: tenant_setting_config
  role: tenant
lifecycle:
- dict: tenant_product__open_status
  process: tenant_product__open_status
```

## 页面链接

- [[tables/tenant_product]]
- [[tables/tenant_setting_config]]
- [[dicts/tenant_product__open_status]]
- [[processes/tenant_product__open_status]]
