---
type: caliber
title: 生效企业
page_key: effective_company
belong: calibers
domain: cust
status: draft
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status,
  cust_company_info.data_type, cust_company_info.enable]
sources: ['code_path:CustCompanyIfoEnchanceService.java:649']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 生效企业

回答「当前有效企业」。必须建档成功且生效同时成立；不要用 BUILD_SUCCESS 单独代替。
不含变更中（CUST_CHANGE + CHANGE）。按角色过滤时走 effective_company_by_role。


```ground:caliber
caliber: 生效企业
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status,
  cust_company_info.data_type, cust_company_info.enable]
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status
  = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable =
  'Y'
scope: global
boundary: '回答「当前有效企业」。必须建档成功且生效同时成立；不要用 BUILD_SUCCESS 单独代替。

  不含变更中（CUST_CHANGE + CHANGE）。按角色过滤时走 effective_company_by_role。

  '
using_relations: []
evidence: code_path:CustCompanyIfoEnchanceService.java:649
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[dicts/cust_company_info__data_type]]
- [[dicts/cust_company_info__enable]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
