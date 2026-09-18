---
type: rule
title: 企业冻结级联角色与管理员 SSO
page_key: freeze_cascade
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.cust_status, cust_role_info.status]
sources: ['code_path:CustCompanyInfoApplication.java:712']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info, cust_role_info]
---

# 企业冻结级联角色与管理员 SSO

freeze：cust_status 从 EFFECT/ADD 写成 FREEZE，角色 status 同步（已 WRITEOFF 跳过），再 freezeCustAdminUsers 冻 FBP 角色的 SSO。
列表冻结入口同时把 cust_company_lifecycle_info.type 写成 FRZ，并写入 reason/attach、enable=Y。
不写 cust_person_info.enable。needCheckInWay 配置为 true，实现是空 TODO，本路径不拦在途。


```ground:rule
rule: 企业冻结级联角色与管理员 SSO
field_targets: [cust_company_info.cust_status, cust_role_info.status]
impact: write_constraint
content: 'freeze：cust_status 从 EFFECT/ADD 写成 FREEZE，角色 status 同步（已 WRITEOFF 跳过），再
  freezeCustAdminUsers 冻 FBP 角色的 SSO。

  列表冻结入口同时把 cust_company_lifecycle_info.type 写成 FRZ，并写入 reason/attach、enable=Y。

  不写 cust_person_info.enable。needCheckInWay 配置为 true，实现是空 TODO，本路径不拦在途。

  '
evidence: code_path:CustCompanyInfoApplication.java:712
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_role_info]]
- [[dicts/cust_company_info__cust_status]]
- [[dicts/cust_role_info__status]]
- [[processes/cust_company_info__cust_status]]
- [[processes/cust_role_info__status]]
