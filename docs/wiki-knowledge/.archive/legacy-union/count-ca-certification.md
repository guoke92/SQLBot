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
title: CA认证有多少
page_key: count-ca-certification
domain: cafee
anchors:
- ca_certification_info
---
# CA认证有多少

问法：CA认证有多少

```ground:pattern
pattern: count-ca-certification
question: CA认证有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM ca_certification_info WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[ca_certification_info]]
