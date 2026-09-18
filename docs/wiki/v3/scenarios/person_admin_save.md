---
type: scenario
title: 保存联系人校验
page_key: person_admin_save
belong: scenarios
domain: cust
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info]
---

# 保存联系人校验

保存联系人校验

```ground:scenario
scenario: person_admin_save
hubs:
- table: cust_person_info
  role: master
```

## 页面链接

- [[tables/cust_person_info]]
