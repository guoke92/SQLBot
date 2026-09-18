---
type: caliber
title: 企业管理员
page_key: company_admin
belong: calibers
domain: cust
status: draft
field_targets: [cust_person_info.user_type, cust_person_info.enable, cust_person_info.ref_cust_company_info]
sources: ['code_path:CustPersonInfoDao.java:40']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info, cust_company_info]
---

# 企业管理员

回答「该企业的管理员」。Java 枚举名是 admin，库值是 accountAdmin。
listCustAdminerByCustCode 不按 company_type 过滤；一角色一管理员校验才加 company_type。
企业冻结不改本口径的 enable；冻旧建新才会把旧管理员 enable 置 N。


```ground:caliber
caliber: 企业管理员
field_targets: [cust_person_info.user_type, cust_person_info.enable, cust_person_info.ref_cust_company_info]
predicate: cust_person_info.user_type = 'accountAdmin' AND cust_person_info.enable
  = 'Y' AND cust_person_info.ref_cust_company_info = :company_code
scope: global
boundary: '回答「该企业的管理员」。Java 枚举名是 admin，库值是 accountAdmin。

  listCustAdminerByCustCode 不按 company_type 过滤；一角色一管理员校验才加 company_type。

  企业冻结不改本口径的 enable；冻旧建新才会把旧管理员 enable 置 N。

  '
using_relations:
- left: cust_company_info.code
  right: cust_person_info.ref_cust_company_info
evidence: code_path:CustPersonInfoDao.java:40
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_person_info]]
- [[dicts/cust_person_info__enable]]
- [[dicts/cust_person_info__user_type]]
