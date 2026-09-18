---
type: caliber
title: 企业宽表服务期内
page_key: in_period_ca_fee_company
belong: calibers
domain: ca_fee
status: draft
field_targets: [ca_fee_company.service_end, ca_fee_company.enable]
sources: ['code_path:CaFeeRuleEngineService.java:268']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_company]
---

# 企业宽表服务期内

规则引擎 isInServicePeriodByCompany：service_end 不早于 today。pay_status 不是本口径条件。

```ground:caliber
caliber: 企业宽表服务期内
field_targets: [ca_fee_company.service_end, ca_fee_company.enable]
predicate: ca_fee_company.enable = 'Y' AND ca_fee_company.service_end >= CURRENT_DATE
scope: global
boundary: 规则引擎 isInServicePeriodByCompany：service_end 不早于 today。pay_status 不是本口径条件。
using_relations: []
evidence: code_path:CaFeeRuleEngineService.java:268
```

## 页面链接

- [[tables/ca_fee_company]]
- [[dicts/ca_fee_company__enable]]
