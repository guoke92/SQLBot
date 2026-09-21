---
type: caliber
title: 已开启 CA 收费的项目
page_key: charge_enabled_project
belong: calibers
domain: ca_fee
status: draft
field_targets: [ca_fee_project_config.charge_enabled, ca_fee_project_config.enable]
sources: ['code_path:CaFeeRuleEngineService.java:98']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_project_config, tenant_project]
---

# 已开启 CA 收费的项目

无配置或 charge_enabled≠Y 时规则引擎 feeStatus=EXEMPT（PROJECT_DISABLED），不是未缴费。

```ground:caliber
caliber: 已开启 CA 收费的项目
field_targets: [ca_fee_project_config.charge_enabled, ca_fee_project_config.enable]
predicate: ca_fee_project_config.charge_enabled = 'Y' AND ca_fee_project_config.enable
  = 'Y'
scope: global
boundary: 无配置或 charge_enabled≠Y 时规则引擎 feeStatus=EXEMPT（PROJECT_DISABLED），不是未缴费。
using_relations:
- left: tenant_project.id
  right: ca_fee_project_config.project_id
evidence: code_path:CaFeeRuleEngineService.java:98
```

## 页面链接

- [[tables/ca_fee_project_config]]
- [[tables/tenant_project]]
- [[dicts/ca_fee_project_config__charge_enabled]]
- [[dicts/ca_fee_project_config__enable]]
