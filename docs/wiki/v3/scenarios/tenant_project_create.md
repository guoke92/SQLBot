---
type: scenario
title: 创建租户项目
page_key: tenant_project_create
belong: scenarios
domain: tenant
status: draft
aliases: [新建项目, 项目配置]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project, tenant_setting_config, tenant_product]
---

# 创建租户项目

创建项目写 tenant_id=租户主键、product_id=租户产品主键、project_status=0。问有效项目用 effective_tenant_project。

```ground:scenario
scenario: tenant_project_create
hubs:
- table: tenant_project
  role: master
shared:
- table: tenant_setting_config
  role: tenant
- table: tenant_product
  role: product
lifecycle:
- dict: tenant_project__project_status
  process: tenant_project__project_status
```

## 页面链接

- [[tables/tenant_product]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]
- [[dicts/tenant_project__project_status]]
- [[processes/tenant_project__project_status]]
