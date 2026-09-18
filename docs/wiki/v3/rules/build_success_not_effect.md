---
type: rule
title: 认证成功不等于生效
page_key: build_success_not_effect
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status]
sources: ['code_path:CustCompanyIfoEnchanceService.java:649']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 认证成功不等于生效

BUILD_SUCCESS 只回答建档/认证是否成功。EFFECT 才是生效。
问「有效企业 / 生效企业」必须套用 effective_company，禁止只过滤 cust_build_status。
运营建档回调先写 BUILD_SUCCESS，再由 effectCust 写 EFFECT，两列可能短暂不一致。


```ground:rule
rule: 认证成功不等于生效
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status]
impact: query_constraint
content: 'BUILD_SUCCESS 只回答建档/认证是否成功。EFFECT 才是生效。

  问「有效企业 / 生效企业」必须套用 effective_company，禁止只过滤 cust_build_status。

  运营建档回调先写 BUILD_SUCCESS，再由 effectCust 写 EFFECT，两列可能短暂不一致。

  '
evidence: code_path:CustCompanyIfoEnchanceService.java:649
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
