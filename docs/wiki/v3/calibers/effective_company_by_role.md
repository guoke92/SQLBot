---
type: caliber
title: 按角色生效的企业
page_key: effective_company_by_role
belong: calibers
domain: cust
status: draft
field_targets: [cust_role_info.role_type, cust_company_info.cust_build_status, cust_company_info.cust_status]
sources: ['code_path:CustCompanyQueryMapper.xml:77']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_role_info, cust_company_info]
---

# 按角色生效的企业

运营按企业角色拉「有效企业」；变更中企业在此口径内，与 effective_company 不同。

```ground:caliber
caliber: 按角色生效的企业
field_targets: [cust_role_info.role_type, cust_company_info.cust_build_status, cust_company_info.cust_status]
predicate: cust_role_info.role_type = :custType AND cust_role_info.enable = 'Y' AND
  cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y' AND ((cust_company_info.cust_build_status
  = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT') OR (cust_company_info.cust_build_status
  = 'CUST_CHANGE' AND cust_company_info.cust_status = 'CHANGE'))
scope: global
boundary: 运营按企业角色拉「有效企业」；变更中企业在此口径内，与 effective_company 不同。
using_relations:
- left: cust_company_info.code
  right: cust_role_info.ref_cust_company_info
evidence: code_path:CustCompanyQueryMapper.xml:77
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_role_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[dicts/cust_role_info__role_type]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
