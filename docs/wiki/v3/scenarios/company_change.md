---
type: scenario
title: 企业变更
page_key: company_change
belong: scenarios
domain: cust
status: draft
aliases: [客户变更, 资料变更]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info, cust_change_record, cust_change_cfg, cust_person_info]
---

# 企业变更

变更把建档状态写成 CUST_CHANGE、生效状态写成 CHANGE。问变更中企业用 changing_company，不要当成失效。

```ground:scenario
scenario: company_change
hubs:
- table: cust_company_info
  role: master
shared:
- table: cust_change_record
  role: change_log
- table: cust_change_cfg
  role: change_item
- table: cust_person_info
  role: admin_person
lifecycle:
- dict: cust_company_info__cust_build_status
  process: cust_company_info__cust_build_status
- dict: cust_company_info__cust_status
  process: cust_company_info__cust_status
- dict: cust_company_info__check_status
  process: cust_company_info__check_status
```

## 页面链接

- [[tables/cust_change_cfg]]
- [[tables/cust_change_record]]
- [[tables/cust_company_info]]
- [[tables/cust_person_info]]
- [[dicts/cust_company_info__check_status]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[processes/cust_company_info__check_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
