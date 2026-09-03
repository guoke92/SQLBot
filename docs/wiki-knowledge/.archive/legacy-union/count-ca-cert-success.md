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
title: 已提交成功的 CA 数字证书认证有多少
page_key: count-ca-cert-success
domain: ca_certification
anchors:
- ca_certification_info
---
# 已提交成功的 CA 数字证书认证有多少

问法：已提交成功的 CA 数字证书认证有多少

```ground:pattern
pattern: count-ca-cert-success
question: 已提交成功的 CA 数字证书认证有多少
sql: "SELECT COUNT(1) AS ca_cert_success_count\nFROM ca_certification_info\nWHERE\
  \ submit_status = 'SUCCESS'\n  AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[ca_certification_info]]
