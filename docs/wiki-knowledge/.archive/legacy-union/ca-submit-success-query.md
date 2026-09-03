---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 企业最新成功报数行
page_key: ca-submit-success-query
domain: CA认证与服务费
anchors:
- ca_certification_info
---
# 企业最新成功报数行

问法：企业最新成功报数行

```ground:pattern
pattern: ca-submit-success-query
question: 企业最新成功报数行
sql: SELECT * FROM ca_certification_info WHERE cust_id = ? AND submit_status = 'SUCCESS'
  AND enable = 'Y' ORDER BY submit_time DESC, id DESC LIMIT 1
verification: PENDING_VALIDATION
```

## 关联
- [[ca_certification_info]]
