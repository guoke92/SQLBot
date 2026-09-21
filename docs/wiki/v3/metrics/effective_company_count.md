---
type: metric
title: 生效企业数
page_key: effective_company_count
belong: metrics
domain: cust
status: draft
sources: ['code_path:CustCompanyIfoEnchanceService.java:647']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [effective_company, cust_company_info]
---

# 生效企业数

```ground:metric
metric: 生效企业数
caliber: effective_company
grain_table: cust_company_info
aggregation: count_distinct
field: cust_company_info.id
using_relations: []
evidence: code_path:CustCompanyIfoEnchanceService.java:647
```

## 页面链接

- [[tables/cust_company_info]]
- [[calibers/effective_company]]
