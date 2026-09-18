---
type: rule
title: 简易认证不开通供票产品
page_key: simple_auth_no_draft_product
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.identify_style, cust_company_info.need_register_ca,
  cust_company_info.head_company]
sources: ['code_path:CustCompanyInfoApplication.java:4437']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 简易认证不开通供票产品

relateProject 时若产品 platform_product_code 以供票前缀开头，则 identify_style 不得为 SIMPLE，且须已开通电子签章、须为总公司。

```ground:rule
rule: 简易认证不开通供票产品
field_targets: [cust_company_info.identify_style, cust_company_info.need_register_ca,
  cust_company_info.head_company]
impact: write_constraint
content: relateProject 时若产品 platform_product_code 以供票前缀开头，则 identify_style 不得为 SIMPLE，且须已开通电子签章、须为总公司。
evidence: code_path:CustCompanyInfoApplication.java:4437
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__head_company]]
- [[dicts/cust_company_info__identify_style]]
- [[dicts/cust_company_info__need_register_ca]]
