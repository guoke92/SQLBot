---
type: caliber
title: 变更中企业
page_key: changing_company
belong: calibers
domain: cust
status: draft
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status,
  cust_company_info.data_type, cust_company_info.enable]
sources: ['code_path:CustCompanyInfoApplication.java:7348']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 变更中企业

回答「正在变更的企业」。不要当成失效或建档失败。
与 effective_company 互斥；effective_company_by_role 会把它算进去。


```ground:caliber
caliber: 变更中企业
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status,
  cust_company_info.data_type, cust_company_info.enable]
predicate: cust_company_info.cust_build_status = 'CUST_CHANGE' AND cust_company_info.cust_status
  = 'CHANGE' AND cust_company_info.data_type = '1' AND cust_company_info.enable =
  'Y'
scope: global
boundary: '回答「正在变更的企业」。不要当成失效或建档失败。

  与 effective_company 互斥；effective_company_by_role 会把它算进去。

  '
using_relations: []
evidence: code_path:CustCompanyInfoApplication.java:7348
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[dicts/cust_company_info__data_type]]
- [[dicts/cust_company_info__enable]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
