---
type: scenario
title: 协议迁移拉取
page_key: agreement_migratory
belong: scenarios
domain: remaining
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [argeement_migratory_record, cust_company_info]
---

# 协议迁移拉取

协议迁移拉取

```ground:scenario
scenario: agreement_migratory
hubs:
- table: argeement_migratory_record
  role: master
shared:
- table: cust_company_info
  role: company
```

## 页面链接

- [[tables/argeement_migratory_record]]
- [[tables/cust_company_info]]
