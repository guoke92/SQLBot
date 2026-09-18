---
type: rule
title: 收费评估按豁免链优先
page_key: ca_fee_evaluate_priority
belong: rules
domain: ca_fee
status: draft
field_targets: [ca_fee_project_config.charge_enabled, ca_fee_company.special_config_flag,
  ca_fee_company.service_end]
sources: ['code_path:CaFeeRuleEngineService.java:56']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_project_config, ca_fee_company]
---

# 收费评估按豁免链优先

evaluate 首个命中即返回：未开收费 → 白名单 → 延期支付 → 服务期内已缴 → 应缴 0 元 → 需缴费。
特殊企业在项目 JSON special_company_list，不是 ca_fee_special_config 表。


```ground:rule
rule: 收费评估按豁免链优先
field_targets: [ca_fee_project_config.charge_enabled, ca_fee_company.special_config_flag,
  ca_fee_company.service_end]
impact: query_constraint
content: 'evaluate 首个命中即返回：未开收费 → 白名单 → 延期支付 → 服务期内已缴 → 应缴 0 元 → 需缴费。

  特殊企业在项目 JSON special_company_list，不是 ca_fee_special_config 表。

  '
evidence: code_path:CaFeeRuleEngineService.java:56
```

## 页面链接

- [[tables/ca_fee_company]]
- [[tables/ca_fee_project_config]]
- [[dicts/ca_fee_company__special_config_flag]]
- [[dicts/ca_fee_project_config__charge_enabled]]
