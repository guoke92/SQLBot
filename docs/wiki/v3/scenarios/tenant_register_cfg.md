---
type: scenario
title: 租户自主注册配置
page_key: tenant_register_cfg
belong: scenarios
domain: tenant
status: draft
aliases: [项目码必填, 默认关联项目]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config, tenant_project]
---

# 租户自主注册配置

租户配置 project_code_required 与 default_project_id。现网必填项目码时必须先有默认项目。

```ground:scenario
scenario: tenant_register_cfg
hubs:
- table: tenant_setting_config
  role: master
shared:
- table: tenant_project
  role: default_project
```

## 页面链接

- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]
