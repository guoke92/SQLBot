---
type: scenario
title: 企业授权确认书
page_key: authorization_agreement
belong: scenarios
domain: remaining
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [authorization_agreement, cust_company_info]
---

# 企业授权确认书

企业授权确认书

```ground:scenario
scenario: authorization_agreement
hubs:
- table: authorization_agreement
  role: master
shared:
- table: cust_company_info
  role: company
```

## 页面链接

- [[tables/authorization_agreement]]
- [[tables/cust_company_info]]
