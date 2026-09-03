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
title: CA认证成功的企业有多少
page_key: count-ca-success
domain: certification
anchors:
- ca_certification_info
---
# CA认证成功的企业有多少

问法：CA认证成功的企业有多少

```ground:pattern
pattern: count-ca-success
question: CA认证成功的企业有多少
sql: 'SELECT COUNT(*) AS ca_success_count

  FROM ca_certification_info

  WHERE submit_status = ''SUCCESS'' AND enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[ca_certification_info]]
