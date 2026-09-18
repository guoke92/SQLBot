---
type: scenario
title: 企业冻结与注销
page_key: company_freeze
belong: scenarios
domain: cust
status: draft
aliases: [冻结企业, 注销企业, 解冻]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info, cust_role_info, cust_company_lifecycle_info]
---

# 企业冻结与注销

冻结写 cust_status=FREEZE 并同步角色 status，再冻管理员 SSO。注销写 WRITEOFF 并冻全部 SSO。
不要问成「管理员 enable=N」。


```ground:scenario
scenario: company_freeze
hubs:
- table: cust_company_info
  role: master
shared:
- table: cust_role_info
  role: company_role
- table: cust_company_lifecycle_info
  role: freeze_audit
lifecycle:
- dict: cust_company_info__cust_status
  process: cust_company_info__cust_status
- dict: cust_role_info__status
  process: cust_role_info__status
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_company_lifecycle_info]]
- [[tables/cust_role_info]]
- [[dicts/cust_company_info__cust_status]]
- [[dicts/cust_role_info__status]]
- [[processes/cust_company_info__cust_status]]
- [[processes/cust_role_info__status]]
