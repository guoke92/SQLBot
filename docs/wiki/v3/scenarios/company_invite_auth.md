---
type: scenario
title: 邀请认证
page_key: company_invite_auth
belong: scenarios
domain: cust
status: draft
aliases: [邀请建档, 平台录入认证, 客户录入认证]
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info, cust_person_info, cust_account_info, cust_build_record,
  cust_certification_info]
---

# 邀请认证

邀请/自主提交走 submitCust，运营回调写 check_status 与 cust_build_status。人员、账户按企业 code 闭包。

```ground:scenario
scenario: company_invite_auth
hubs:
- table: cust_company_info
  role: master
shared:
- table: cust_person_info
  role: admin_person
- table: cust_account_info
  role: bank_account
- table: cust_build_record
  role: oper_push
- table: cust_certification_info
  role: license
lifecycle:
- dict: cust_company_info__cust_build_status
  process: cust_company_info__cust_build_status
- dict: cust_company_info__check_status
  process: cust_company_info__check_status
```

## 页面链接

- [[tables/cust_account_info]]
- [[tables/cust_build_record]]
- [[tables/cust_certification_info]]
- [[tables/cust_company_info]]
- [[tables/cust_person_info]]
- [[dicts/cust_company_info__check_status]]
- [[dicts/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__check_status]]
- [[processes/cust_company_info__cust_build_status]]
