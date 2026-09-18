---
type: rule
title: 简易认证强制不开通电子签章
page_key: simple_auth_no_ca
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.identify_style, cust_company_info.need_register_ca,
  cust_company_info.ca_register_status, cust_company_info.need_register_bs, cust_company_info.bs_register_status]
sources: ['code_path:CustCompanyCaPolicy.java:26']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 简易认证强制不开通电子签章

identify_style=SIMPLE 时 CustCompanyCaPolicy 把 need_register_ca / ca_register_status / need_register_bs / bs_register_status 全部写成 N。
简易提交若历史标记需开通 CA，会先校正再落库。与 simple_auth_no_draft_product（供票产品约束）不是同一条。


```ground:rule
rule: 简易认证强制不开通电子签章
field_targets: [cust_company_info.identify_style, cust_company_info.need_register_ca,
  cust_company_info.ca_register_status, cust_company_info.need_register_bs, cust_company_info.bs_register_status]
impact: write_constraint
content: 'identify_style=SIMPLE 时 CustCompanyCaPolicy 把 need_register_ca / ca_register_status
  / need_register_bs / bs_register_status 全部写成 N。

  简易提交若历史标记需开通 CA，会先校正再落库。与 simple_auth_no_draft_product（供票产品约束）不是同一条。

  '
evidence: code_path:CustCompanyCaPolicy.java:26
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__bs_register_status]]
- [[dicts/cust_company_info__ca_register_status]]
- [[dicts/cust_company_info__identify_style]]
- [[dicts/cust_company_info__need_register_bs]]
- [[dicts/cust_company_info__need_register_ca]]
