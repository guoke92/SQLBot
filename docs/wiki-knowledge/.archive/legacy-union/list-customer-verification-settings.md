---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:customer-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 客户认证审核配置是什么
page_key: list-customer-verification-settings
domain: config
anchors:
- cust_setting_config
---
# 客户认证审核配置是什么

问法：客户认证审核配置是什么

```ground:pattern
pattern: list-customer-verification-settings
question: 客户认证审核配置是什么
sql: "SELECT cust_id, need_auth_verify, need_verify_no_key, face_recognition,\n  \
  \     payment_verification\nFROM cust_setting_config"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_setting_config]]
