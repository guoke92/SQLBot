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
type: caliber
title: CA认证中
page_key: CA认证中
domain: certification
field_targets:
- ca_certification_info.submit_status
---
# CA认证中

submit_status 等于物理值 PENDING 的记录。

```ground:caliber
caliber: CA认证中
field_targets:
- ca_certification_info.submit_status
filters:
- .ca_cert.submit_status = 'PENDING'
```

## 关联
- [[ca_certification_info]]
