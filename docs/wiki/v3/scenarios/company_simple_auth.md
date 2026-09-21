---
type: scenario
title: 简易认证提交
page_key: company_simple_auth
belong: scenarios
domain: cust
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# 简易认证提交

简易认证提交

```ground:scenario
scenario: company_simple_auth
hubs:
- table: cust_company_info
  role: master
```

## 页面链接

- [[tables/cust_company_info]]
