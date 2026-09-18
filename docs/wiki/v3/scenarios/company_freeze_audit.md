---
type: scenario
title: 冻结解冻留痕
page_key: company_freeze_audit
belong: scenarios
domain: cust
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_lifecycle_info]
---

# 冻结解冻留痕

冻结解冻留痕

```ground:scenario
scenario: company_freeze_audit
hubs:
- table: cust_company_lifecycle_info
  role: master
```

## 页面链接

- [[tables/cust_company_lifecycle_info]]
