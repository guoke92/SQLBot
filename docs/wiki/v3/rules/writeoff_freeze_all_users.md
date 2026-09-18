---
type: rule
title: 企业注销冻结全部 SSO 用户
page_key: writeoff_freeze_all_users
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.cust_status, cust_role_info.status]
sources: ['code_path:CustCompanyInfoApplication.java:901']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info, cust_role_info]
---

# 企业注销冻结全部 SSO 用户

diable：cust_status 从 EFFECT 写成 WRITEOFF，角色 status 同步，再 freezeCustAllUsers 冻结该企业全部 SSO 用户。
与冻结只冻管理员不同。


```ground:rule
rule: 企业注销冻结全部 SSO 用户
field_targets: [cust_company_info.cust_status, cust_role_info.status]
impact: write_constraint
content: 'diable：cust_status 从 EFFECT 写成 WRITEOFF，角色 status 同步，再 freezeCustAllUsers
  冻结该企业全部 SSO 用户。

  与冻结只冻管理员不同。

  '
evidence: code_path:CustCompanyInfoApplication.java:901
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_role_info]]
- [[dicts/cust_company_info__cust_status]]
- [[dicts/cust_role_info__status]]
- [[processes/cust_company_info__cust_status]]
- [[processes/cust_role_info__status]]
