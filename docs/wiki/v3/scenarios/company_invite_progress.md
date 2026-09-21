---
type: scenario
title: 邀请进度
page_key: company_invite_progress
belong: scenarios
domain: cust
status: draft
aliases: [邀请建档进度]
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_invite_info, cust_company_info]
---

# 邀请进度

邀请落库 progress=INIT。之后按被邀请企业名称+租户把 progress 写成 cust_build_status。
邀请方企业用 invite_cust_id=company.id；不要用这条 JOIN 解释 progress。


```ground:scenario
scenario: company_invite_progress
hubs:
- table: cust_invite_info
  role: master
shared:
- table: cust_company_info
  role: invited_company
lifecycle:
- dict: cust_invite_info__progress
  process: cust_invite_info__progress
- dict: cust_company_info__cust_build_status
  process: cust_company_info__cust_build_status
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_invite_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_invite_info__progress]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_invite_info__progress]]
