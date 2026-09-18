---
type: process
title: 企业角色状态
page_key: cust_role_info__status
belong: processes
domain: cust
status: draft
anchors: [cust_role_info.status]
field_targets: [cust_role_info.status]
sources: ['code_path:CustRoleApplication.java:112']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_role_info]
---

# 企业角色状态

钉 cust_role_info.status。企业冻结/注销/解冻时按 code 批量同步为企业 cust_status；已 WRITEOFF 的角色不再改。


```ground:process
process: 企业角色状态
field: cust_role_info.status
entry: CustRoleApplication.updateStatusByCustCompany
stages:
- stage: 随企业状态
  transitions:
  - from: EFFECT
    event: 企业冻结
    to: FREEZE
    evidence: code_path:CustRoleApplication.java:112
  - from: EFFECT
    event: 企业注销
    to: WRITEOFF
    evidence: code_path:CustRoleApplication.java:112
  - from: FREEZE
    event: 企业解冻
    to: EFFECT
    evidence: code_path:CustRoleApplication.java:112
```

## 页面链接

- [[tables/cust_role_info]]
- [[dicts/cust_role_info__status]]
