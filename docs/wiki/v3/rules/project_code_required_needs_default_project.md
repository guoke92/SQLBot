---
type: rule
title: 项目码必填时必须先配默认关联项目
page_key: project_code_required_needs_default_project
belong: rules
domain: tenant
status: draft
field_targets: [tenant_setting_config.project_code_required, tenant_setting_config.default_project_id]
sources: ['code_path:TenantDomainService.java:234']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config]
---

# 项目码必填时必须先配默认关联项目

现网：project_code_required=Y 时 default_project_id 不能空。
V1.28 需求写的是「项目码必填则默认关联项目非必填」。以代码为准。


```ground:rule
rule: 项目码必填时必须先配默认关联项目
field_targets: [tenant_setting_config.project_code_required, tenant_setting_config.default_project_id]
impact: write_constraint
content: '现网：project_code_required=Y 时 default_project_id 不能空。

  V1.28 需求写的是「项目码必填则默认关联项目非必填」。以代码为准。

  '
evidence: code_path:TenantDomainService.java:234
```

## 页面链接

- [[tables/tenant_setting_config]]
- [[dicts/tenant_setting_config__project_code_required]]
