---
type: scenario
title: 企业管理员
page_key: person_admin
belong: scenarios
domain: cust
status: draft
aliases: [客户管理员, 冻旧建新]
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info, cust_company_info, cust_oper_change_record]
---

# 企业管理员

管理员钉 user_type=accountAdmin 且 enable=Y。同一企业同一 company_type 只能有一个有效管理员。
变更管理员是冻旧建新，不是改原行。企业冻结不改 person.enable。


```ground:scenario
scenario: person_admin
hubs:
- table: cust_person_info
  role: master
shared:
- table: cust_company_info
  role: company
- table: cust_oper_change_record
  role: oper_trace
lifecycle:
- dict: cust_person_info__user_type
- dict: cust_person_info__status
  process: cust_person_info__status
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_oper_change_record]]
- [[tables/cust_person_info]]
- [[dicts/cust_person_info__status]]
- [[dicts/cust_person_info__user_type]]
- [[processes/cust_person_info__status]]
