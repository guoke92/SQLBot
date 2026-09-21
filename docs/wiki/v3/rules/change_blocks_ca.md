---
type: rule
title: 变更中禁止开通电子签章
page_key: change_blocks_ca
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.cust_build_status, cust_company_info.need_register_ca]
sources: ['code_path:CustCompanyIfoEnchanceService.java:786']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# 变更中禁止开通电子签章

cust_build_status=CUST_CHANGE 时 isOpenCa 返回阻断文案，不进入开通。
与简易认证强制 N 不同：这是变更在途拦截，不是认证方式策略。


```ground:rule
rule: 变更中禁止开通电子签章
field_targets: [cust_company_info.cust_build_status, cust_company_info.need_register_ca]
impact: write_constraint
content: 'cust_build_status=CUST_CHANGE 时 isOpenCa 返回阻断文案，不进入开通。

  与简易认证强制 N 不同：这是变更在途拦截，不是认证方式策略。

  '
evidence: code_path:CustCompanyIfoEnchanceService.java:786
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__need_register_ca]]
- [[processes/cust_company_info__cust_build_status]]
