---
type: scenario
title: 冻结企业
page_key: company_freeze_submit
belong: scenarios
domain: cust
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 冻结企业

冻结企业

```ground:scenario
scenario: company_freeze_submit
hubs:
- table: cust_company_info
  role: master
```

## 页面链接

- [[tables/cust_company_info]]
